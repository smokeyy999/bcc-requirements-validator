"""Split a large structured review into model decisions bound to existing claim IDs."""
from copy import deepcopy
import re

from . import engine as e
from .metrics import purpose


FOCI = {
    "business_rules": "Найди несовместимые обязательства для одних входных условий, в том числе при повторном прохождении состояния.",
    "examples": "Вручную выполни каждый приёмочный пример по общим правилам, включая единицы, даты и состояние. Сопоставь ожидаемые результаты.",
    "interfaces": "Проследи заявленные операции между интерфейсами, разрешённые эффекты, статусы, тела ошибок и примеры.",
    "data_flow": "Для каждого отдельного значения, которое должен видеть пользователь или другая система, найди его источник и способ получения.",
}


def _checked(provider, prompt, schema, check):
    """Repeat only this unaccepted piece with the same schema and complete source."""
    feedback = ""
    for attempt in range(2):
        if attempt:
            with purpose("validation_patch"):
                answer = provider.ask(prompt + feedback, schema)
        else:
            answer = provider.ask(prompt, schema)
        try:
            e.validate(answer, schema)
            return check(answer)
        except ValueError as exc:
            if attempt:
                raise ValueError(f"Gemini не исправил возвращённые записи: {exc}") from exc
            feedback = "\nИсправь указанные ошибки. Сохрани полноту, используй только существующие ID. " + str(exc)


def _check_findings(provider, raw, payload, by_id, blocks, references):
    good = list(raw)
    errors = {}
    for i, row in enumerate(raw):
        try:
            e._finding(row, by_id, blocks, references)
        except ValueError as exc:
            errors[f"f{i}"] = {"row": row, "error": str(exc)}
    if not errors:
        return good
    schema = e.obj(**{key: e.FINDING for key in errors})
    prompt = ("Исправь только перечисленные замечания по переданному исходнику и проверенным утверждениям. "
              "quote оставь пустой, если достаточно проверенной цитаты ID. Сохрани все данные каждой карточки. "
              "Возвращай только исправленные карточки по данным ключам.\n" + e.compact({"source": payload, "errors": errors}))
    def verify(answer):
        for key, row in answer.items():
            e._finding(row, by_id, blocks, references)
        return answer
    with purpose("finding_repair"):
        corrected = _checked(provider, prompt, schema, verify)
    for key, row in corrected.items():
        good[int(key[1:])] = row
    return good


def cross_review(provider, payload, claims, blocks, required, references, progress):
    by_id = {c["id"]: c for c in claims}
    claim_id = e.enum(*by_id) if by_id else e.STR
    head_schema = e.obj(reviews=e.obj(**{key: e.array(e.FINDING) for key in FOCI}),
                        scope=e.obj(operations=e.STR, values=e.STR), assessment=e.STR,
                        extra_operations=e.array(claim_id), extra_values=e.array(claim_id),
                        readiness=e.STR, priorities=e.array(e.STR))
    head_prompt = (e.SYNTHESIZE + "\nНа этом проходе заполни все четыре независимых направления reviews. "
                   "Проверь каждый пример и переходы, не останавливайся на первой найденной причине. "
                   "Связи и разрешения по каждому ID будут обработаны отдельным проходом. В extra_operations "
                   "и extra_values перечисли дополнительные ID операций и источников, которых нет в required_traces. "
                   "В evidence и interpretations используй id и quote=пустая строка для проверенного текста.\n"
                   + e.compact({"directions": FOCI, "input": payload}))
    def validate_head(answer):
        e._nonempty(answer, "assessment", "readiness")
        e._nonempty(answer["scope"], "operations", "values")
        for field in ("extra_operations", "extra_values"):
            if set(answer[field]) - by_id.keys():
                raise ValueError(f"{field}: разрешены только ID из реестра утверждений.")
        return answer
    head = _checked(provider, head_prompt, head_schema, validate_head)
    findings = _check_findings(provider, [f for group in head["reviews"].values() for f in group],
                               payload, by_id, blocks, references)
    traces, resolved, examples = [], [], []
    required = {e.OPERATION: list(dict.fromkeys(required[e.OPERATION] + head["extra_operations"])),
                e.VALUE: list(dict.fromkeys(required[e.VALUE] + head["extra_values"]))}
    tasks = [(aspect, subject) for aspect, subjects in required.items() for subject in subjects]
    for claim in claims:
        block = blocks[claim["block"]]
        if (getattr(block, "kind", None) == "code" or
                re.search(r"при[её]мк|пример|ожидаемый результат|acceptance|example|expected result",
                          block.section, flags=re.I)):
            tasks.append(("проверка примера", claim["id"]))
    linked = {ev["id"] for row in findings for ev in row["evidence"]}
    tasks.extend(("проверка локальной гипотезы", c["id"]) for c in claims if c["status"] != "проверяемо" and c["id"] not in linked)
    answer_schema = e.obj(reason=e.STR, supports=e.array(claim_id), finding_topic=e.STR)
    for offset in range(0, len(tasks), 10):
        batch = {f"q{i}": {"aspect": aspect, "subject": subject} for i, (aspect, subject) in enumerate(tasks[offset:offset+10])}
        available = {row["topic"]: [ev["id"] for ev in row["evidence"]] for row in findings}
        prompt = (e.SYNTHESIZE + "\nНа этом проходе решение по КАЖДОМУ ключу задач обязательно. Везде reason "
                  "объясняет проверяемую связь по приведённым ID, supports перечисляет реальные ID утверждений. "
                  "Если показана открытая проблема, используй точный finding_topic существующего замечания "
                  "или опиши новую полноценную карточку в new_findings. Указывая тему, ты явно подтверждаешь "
                  "привязку subject задачи как доказательства этой карточки. Для закрытия укажи конкретные "
                  "поддерживающие ID и оставь finding_topic пустым. Само требование о показе значения "
                  "не доказывает, что описан его источник. Для каждого закрытия поясни, что даёт ответ. "
                  "Для задачи «проверка примера» сначала вычисли ожидаемый результат по общему правилу, "
                  "затем прочти результат этого примера при тех же входах. Назови в reason оба результата "
                  "и их условия. Если какое-то условие неизвестно, объясни зависимость. Для контракта "
                  "различай документированный частный случай, общий случай и заголовок подраздела. "
                  "В новой карточке quote=пустая строка означает взять проверенную цитату ID.\n"
                  + e.compact({"source": payload, "existing_topics": available, "tasks": batch}))

        progress(f"Сквозные связи Gemini: проверок {offset+1}–{offset+len(batch)} из {len(tasks)}.")
        pending, decisions = list(batch), {}
        for attempt in range(2):
            schema = e.obj(decisions=e.obj(**{key: answer_schema for key in pending}), new_findings=e.array(e.FINDING))
            if attempt:
                prompt += ("\nПовтори только решения для " + str(pending) + ". Нужны реальные ID оснований "
                           "и точная тема одного из доступных замечаний либо явное закрытие. Доступные темы: "
                           + e.compact(list(available)))
                with purpose("decision_repair"):
                    answer = provider.ask(prompt, schema)
            else:
                answer = provider.ask(prompt, schema)
            if (not isinstance(answer, dict) or set(answer) != {"decisions", "new_findings"}
                    or not isinstance(answer["decisions"], dict) or set(answer["decisions"]) - set(pending)):
                raise ValueError("Gemini вернул запись вне запрошенных ключей.")
            e.validate(answer["new_findings"], e.array(e.FINDING))
            new = _check_findings(provider, answer["new_findings"], payload, by_id, blocks, references)
            for finding in new:
                if finding not in findings:
                    findings.append(finding)
                available[finding["topic"]] = [ev["id"] for ev in finding["evidence"]]
            for key, decision in answer["decisions"].items():
                try:
                    e.validate(decision, answer_schema)
                except ValueError:
                    continue  # повторим только невалидное поле
                supports, topic = set(decision["supports"]), decision["finding_topic"]
                if (decision["reason"].strip() and supports <= by_id.keys()
                        and (topic in available if topic else bool(supports))):
                    decisions[key] = decision
            pending = [key for key in pending if key not in decisions]
            if not pending:
                break
        if pending:
            raise ValueError(f"Gemini не подтвердил связи с источником для {pending}. Повторите прогон.")
        for key, decision in decisions.items():
            task = batch[key]
            subject, aspect = task["subject"], task["aspect"]
            topic = decision["finding_topic"]
            if topic:
                finding = next(f for f in findings if f["topic"] == topic)
                if subject not in [ev["id"] for ev in finding["evidence"]]:
                    finding["evidence"].append({"id": subject, "quote": ""})
            if aspect in required:
                traces.append({"aspect": aspect, "subjects": [subject], "supports": decision["supports"],
                               "reasoning": decision["reason"], "finding_topic": topic})
            elif aspect == "проверка примера":
                examples.append({"subject": subject, **decision})
            elif not topic:
                resolved.append({"id": subject, "reason": decision["reason"]})
    raw = {key: deepcopy(head[key]) for key in ("scope", "assessment", "readiness", "priorities")}
    raw.update(findings=findings, traces=traces, resolved=resolved)
    e.validate(raw, e.GLOBAL)
    accepted, reasons, checked = e._set_result(raw, claims, blocks, required, references, merge_review_directions=True)
    checked["examples"] = examples
    return accepted, reasons, checked


def audit_review(provider, payload, candidates, claims, progress):
    originals = {f["id"]: f for f in candidates}
    keys = list(originals)
    fields = {"case_scope": e.enum("те же условия", "частный случай", "разные условия", "заголовок", "не установлено", "другая проверка"),
              "scope_reason": e.STR}
    fields.update({k: v for k, v in e.DECISION["properties"].items() if k not in ("id", "question_mode")})
    decisions = {}
    for offset in range(0, len(keys), 6):
        targets = keys[offset:offset + 6]
        errors = {}
        for attempt in range(2):
            schema = e.obj(**{key: e.obj(**fields) for key in targets})
            prompt = (e.ADJUDICATE + "\nВерни решения только по указанным ключам. Остальные доступные карточки "
                      "служат контекстом для устранения дублей. Для подтверждённого дефекта оставляй прямое "
                      "основание только при поддержке обеих сторон исходником. Верни окончательные question и test "
                      "для каждой принятой карточки, сохранив прежний текст или сформулировав новый. При снятии "
                      "оставь оба поля пустыми, blocking=false и supports=[]. Для action=уточнить укажи "
                      "реальные supports из доказательств этой карточки и сформулируй новый вопрос с тестом. "
                      "Перед решением независимо определи case_scope. Если это конфликт, сопоставь точные "
                      "предусловия двух предписаний. В scope_reason назови их и объясни, относятся ли оба "
                      "несовместимых исхода к одному действию. Частное исключение и текст заголовка "
                      "сами по себе не доказывают конфликт поведения. "
                      "Для action=оставить supports=[]. Вывод по набору "
                      "будут оформлены отдельно.\n" + e.compact({"source": payload, "targets": targets, "errors": errors}))
            if attempt:
                with purpose("audit_repair"):
                    answer = provider.ask(prompt, schema)
            else:
                answer = provider.ask(prompt, schema)
            e.validate(answer, schema)
            errors = {}
            for key, value in answer.items():
                item = {k: v for k, v in value.items() if k not in ("case_scope", "scope_reason")}
                item["id"] = key
                # The wire schema expresses the effective question directly. Encode that exact
                # decision into the shared adjudicator's delta representation.
                if not item["question"] and not item["test"]:
                    item["question_mode"] = "убрать"
                elif (item["action"] != "уточнить" and item["question"] == originals[key]["question"]
                      and item["test"] == originals[key]["test"]):
                    item.update(question_mode="сохранить", question="", test="")
                else:
                    item["question_mode"] = "заменить"
                try:
                    e._nonempty(value, "scope_reason")
                    if (originals[key]["kind"] == "Дефект" and originals[key]["category"] == "Противоречивость"
                            and item["action"] == "оставить" and value["case_scope"] != "те же условия"):
                        raise ValueError("Для конфликта поведения нужны несовместимые исходы при одинаковых условиях. "
                                         "Если область различается, сними замечание или уточни открытый вопрос.")
                    e._adjudicate_one(item, originals[key])
                except ValueError as exc:
                    errors[key] = str(exc)
                else:
                    decisions[key] = item
            targets = list(errors)
            if not targets:
                break
        if errors:
            raise ValueError("Проверка вердиктов Gemini: " + e.compact(errors))
    ordered = [decisions[key] for key in keys]
    kept = [key for key in keys if decisions[key]["action"] != "снять"]
    summary_schema = e.obj(assessment=e.STR, readiness=e.STR,
                           priorities=e.array(e.obj(ids=e.array(e.enum(*kept) if kept else e.STR), step=e.STR)))
    prompt = (e.ADJUDICATE + "\nРешения уже приняты по полному ТЗ. Составь вывод, готовность и порядок "
              "работ, опираясь на оставшиеся карточки. Для каждого шага укажи ID из kept. Если список пуст, "
              "верни пустой priorities.\n" + e.compact({"source": payload, "decisions": ordered, "kept": kept}))
    def finish(answer):
        audit = dict(answer, decisions=ordered)
        e.validate(audit, e.AUDIT)
        return e._final_decisions(audit, candidates, claims)
    return _checked(provider, prompt, summary_schema, finish)
