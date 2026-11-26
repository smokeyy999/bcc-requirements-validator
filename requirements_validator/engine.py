"""Выделение правил, сквозное ревью и проверка доказательств до записи отчёта."""

import json
import re
from .prompts import EXTRACT, SYNTHESIZE


def obj(**fields):
    return {"type": "object", "properties": fields, "required": list(fields),
            "additionalProperties": False}


def array(item):
    return {"type": "array", "items": item}


def enum(*values):
    return {"type": "string", "enum": list(values)}


STR = {"type": "string"}
BOOL = {"type": "boolean"}
LOCAL = obj(
    claims=array(obj(block=STR, quote=STR, summary=STR, assessment=STR,
                     status=enum("проверяемо", "проверить", "недостаточно данных"))),
    context=array(obj(block=STR, role=enum("метаданные", "контекст", "шаблон", "оформление"))),
)
FINDING = obj(
    topic=STR, kind=enum("Дефект", "Неоднозначность", "Предполагаемый пробел", "Рекомендация"),
    category=enum("Ясность", "Однозначность", "Полнота", "Проверяемость", "Противоречивость",
                  "Ограничение решения", "Трассируемость", "Дублирование", "Выполнимость"),
    severity=enum("Критичная", "Существенная", "Низкая"), reason=STR, scenario=STR,
    consequence=STR, evidence=array(obj(id=STR, quote=STR)),
    interpretations=array(obj(id=STR, quote=STR, reading=STR, effect=STR)),
    question=STR, test=STR, blocking=BOOL, fix=STR,
)
GLOBAL = obj(findings=array(FINDING), resolved=array(obj(id=STR, reason=STR)),
             assessment=STR, readiness=STR, priorities=array(STR))


def validate(value, schema, path="ответ"):
    """Подмножество JSON Schema, используемое в обоих протоколах."""
    expected = schema["type"]
    if type(value) is not {"string": str, "object": dict, "array": list, "boolean": bool}[expected]:
        raise ValueError(f"{path}: требуется {expected}")
    if "enum" in schema and value not in schema["enum"]:
        raise ValueError(f"{path}: значение вне списка допустимых")
    if expected == "object":
        if value.keys() != schema["properties"].keys():
            missing = schema["properties"].keys() - value.keys()
            extra = value.keys() - schema["properties"].keys()
            raise ValueError(f"{path}: отсутствуют поля {sorted(missing)}, лишние {sorted(extra)}")
        for field, subschema in schema["properties"].items():
            validate(value[field], subschema, f"{path}.{field}")
    if expected == "array":
        for index, item in enumerate(value):
            validate(item, schema["items"], f"{path}[{index}]")


def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _request(provider, instruction, payload, schema, parse, progress):
    prompt = instruction + "\n\nВход (JSON):\n" + compact(payload)
    correction = ""
    for attempt in range(2):
        # Ошибки аутентификации, сети и квоты обрабатывает транспорт.
        result = provider.ask(prompt + correction, schema)
        try:
            validate(result, schema)
            return parse(result)
        except ValueError as error:
            if attempt:
                raise ValueError(f"Повторный ответ модели не прошёл проверку: {error}. "
                                 "Повторите прогон или смените модель.") from error
            progress("Ответ не прошёл проверку. Запрошено одно исправление.")
            correction = ("\n\nПредыдущий ответ отклонён. Построй полный объект заново. "
                          "Исправь ошибку проверки: " + str(error))


def _nonempty(record, *names):
    for name in names:
        if not record[name].strip():
            raise ValueError(f"Поле {name} не должно быть пустым")


def _canon(text):
    return " ".join(re.findall(r"\w+", text.casefold()))


def _source(block):
    return {"id": block.id, "section": block.section, "source_id": block.source_id,
            "text": block.text}


def _batches(blocks):
    # Блок целиком попадает ровно в один запрос, в том числе таблица или пример.
    batch, size = [], 0
    for block in blocks:
        cost = len(compact(_source(block)))
        if batch and (size + cost > 11500 or len(batch) >= 48):
            yield batch
            batch, size = [], 0
        batch.append(block)
        size += cost
    if batch:
        yield batch


def _extract_block(result, block):
    validate(result, LOCAL)
    if result["context"]:
        if len(result["context"]) != 1 or result["claims"]:
            raise ValueError(f"Двойная классификация блока {block.id}")
        return [], result["context"]
    if not result["claims"]:
        raise ValueError(f"Нет решения для блока {block.id}")
    unique = {}
    for row in result["claims"]:
        _nonempty(row, "quote", "summary", "assessment")
        if row["quote"] not in block.text:
            raise ValueError(f"Цитата утверждения не найдена в блоке {block.id}")
        unique.setdefault((row["quote"], _canon(row["summary"])), row)
    rows = sorted(unique.values(), key=lambda r: (block.text.index(r["quote"]), r["quote"], r["summary"]))
    claims = [dict(row, id=f"R-{block.id}-{index:02}", source_id=block.source_id,
                   location=block.location, section=block.section, findings=[])
              for index, row in enumerate(rows, 1)]
    return claims, []


def _local_parts(result, targets):
    # Провайдер мог вернуть сломанный контейнер: отдельные записи тогда нельзя
    # надёжно отделить. Не принимать ни одной его части без проверки схемы.
    if (not isinstance(result, dict) or result.keys() != {"claims", "context"}
            or not all(isinstance(rows, list) for rows in result.values())):
        return {}, {b.id: "Нужен объект с массивами claims и context" for b in targets}, 0
    grouped = {b.id: {"claims": [], "context": []} for b in targets}
    outside = 0
    for field, rows in result.items():
        for row in rows:
            ident = row.get("block") if isinstance(row, dict) else None
            if isinstance(ident, str) and ident in grouped:
                grouped[ident][field].append(row)
            else:
                outside += 1
    verified, errors = {}, {}
    for block in targets:
        try:
            verified[block.id] = _extract_block(grouped[block.id], block)
        except ValueError as error:
            errors[block.id] = str(error)
    return verified, errors, outside


def _local_review(provider, batch, all_blocks, progress):
    payload = {"blocks": [_source(b) for b in batch]}
    accepted = {}
    targets = batch
    for attempt in range(2):
        result = provider.ask(EXTRACT + "\n\nВход (JSON):\n" + compact(payload), LOCAL)
        valid, errors, outside = _local_parts(result, targets)
        accepted.update(valid)
        if outside:
            progress(f"Отклонены записи без ID запрошенного блока: {outside}.")
        if not errors:
            break
        if attempt:
            details = "; ".join(f"{key}: {value}" for key, value in errors.items())
            raise ValueError(f"Повторный ответ модели не прошёл проверку: {details}. "
                             "Повторите прогон или смените модель.")
        targets = [b for b in targets if b.id in errors]
        progress(f"Повторная разметка блоков: {len(targets)} из {len(batch)}. "
                 "Остальные блоки прошли проверку.")
        neighbours = set()
        for i, b in enumerate(all_blocks):
            if b.id in errors:
                neighbours.update(range(max(0, i - 1), min(len(all_blocks), i + 2)))
        payload = {
            "blocks": [_source(b) for b in targets],
            "context_only": [_source(all_blocks[i]) for i in sorted(neighbours)
                             if all_blocks[i].id not in errors],
            "errors": errors,
        }
    claims, context = [], []
    for b in batch:
        rows, ignored = accepted[b.id]
        claims.extend(rows)
        context.extend(ignored)
    return claims, context


def _evidence(item, by_id, blocks):
    claim = by_id.get(item["id"])
    if not claim:
        raise ValueError(f"Неизвестный ID требования {item['id']}")
    block = blocks[claim["block"]]
    quote = item["quote"] or claim["quote"]
    if not quote.strip() or quote not in block.text:
        raise ValueError(f"Цитата не найдена в источнике для {claim['id']}")
    # Привязка к конкретному правилу внутри общего исходного пункта.
    def occurrences(part):
        return [(m.start(), m.start() + len(part))
                for m in re.finditer(re.escape(part), block.text)]
    if not any(a < d and c < b for a, b in occurrences(quote)
               for c, d in occurrences(claim["quote"])):
        raise ValueError(f"Цитата относится к другой части блока {claim['id']}")
    return {"id": claim["id"], "block": block.id, "quote": quote, "section": block.section,
            "location": block.location}


def _finding(raw, by_id, blocks):
    _nonempty(raw, "topic", "reason", "scenario", "consequence")
    evidence = []
    for item in raw["evidence"]:
        anchor = _evidence(item, by_id, blocks)
        if anchor not in evidence:
            evidence.append(anchor)
    ids = sorted({a["id"] for a in evidence})
    if not ids:
        raise ValueError(f"Нет доказательства для замечания «{raw['topic']}»")
    if raw["category"] == "Противоречивость" and raw["kind"] == "Дефект" and len(ids) < 2:
        raise ValueError("Для противоречия нужны две стороны с разными ID утверждений")
    interpretations = []
    alternatives = raw["interpretations"]
    if raw["kind"] == "Неоднозначность":
        if len(alternatives) != 2:
            raise ValueError("Для неоднозначности нужны две обоснованные трактовки")
        for alternative in alternatives:
            _nonempty(alternative, "reading", "effect")
            anchor = _evidence(alternative, by_id, blocks)
            if anchor["id"] not in ids:
                raise ValueError("Трактовка привязана к постороннему требованию")
            if anchor not in evidence:
                evidence.append(anchor)
            interpretations.append(f"{alternative['reading']} → {alternative['effect']} "
                                   f"({anchor['id']}, «{anchor['quote']}»)")
        if any(_canon(alternatives[0][k]) == _canon(alternatives[1][k])
               for k in ("reading", "effect")):
            raise ValueError("У трактовок должны различаться смысл и последствия")
    elif alternatives:
        raise ValueError("Трактовки следует указывать только для неоднозначности")
    has_question = bool(raw["question"].strip())
    if has_question != bool(raw["test"].strip()) or (raw["blocking"] and not has_question):
        raise ValueError("Свяжи вопрос с конкретным зависимым тестом")
    if raw["kind"] in {"Неоднозначность", "Предполагаемый пробел"} and not has_question:
        raise ValueError("Для открытого бизнес-решения нужен вопрос и зависящий от него тест")
    if raw["kind"] == "Дефект" and not (has_question or raw["fix"].strip()):
        raise ValueError("Для дефекта нужен вопрос или обоснованное исправление")
    return dict(raw, ids=ids, evidence=evidence, interpretations=interpretations,
                counted=raw["kind"] in {"Дефект", "Неоднозначность"})


SEVERITIES = ["Критичная", "Существенная", "Низкая"]


def _merge(findings):
    """Свести повтор одной причины, сохранив ссылки с обеих сторон."""
    unique = []
    for finding in findings:
        anchors = {(a["id"], a["quote"]) for a in finding["evidence"]}
        for previous in unique:
            other = {(a["id"], a["quote"]) for a in previous["evidence"]}
            same_topic = _canon(previous["topic"]) == _canon(finding["topic"])
            same_case = _canon(previous["scenario"]) == _canon(finding["scenario"])
            if (previous["kind"] == finding["kind"] and previous["category"] == finding["category"]
                    and anchors & other and (same_topic or (anchors == other and same_case))):
                previous["ids"] = sorted(set(previous["ids"]) | set(finding["ids"]))
                previous["evidence"].extend(a for a in finding["evidence"] if a not in previous["evidence"])
                previous["blocking"] |= finding["blocking"]
                if SEVERITIES.index(finding["severity"]) < SEVERITIES.index(previous["severity"]):
                    previous["severity"], previous["reason"] = finding["severity"], finding["reason"]
                if finding["question"] and not previous["question"]:
                    previous["question"], previous["test"] = finding["question"], finding["test"]
                break
        else:
            unique.append(finding)
    unique.sort(key=lambda f: (SEVERITIES.index(f["severity"]), f["ids"], f["topic"]))
    for index, finding in enumerate(unique, 1):
        finding["id"] = f"Z-{index:03}"
    return unique


def _set_result(raw, claims, blocks):
    _nonempty(raw, "assessment", "readiness")
    if any(not step.strip() for step in raw["priorities"]):
        raise ValueError("Пустой шаг в порядке исправлений")
    by_id = {c["id"]: c for c in claims}
    findings = _merge([_finding(f, by_id, blocks) for f in raw["findings"]])
    if findings and not raw["priorities"]:
        raise ValueError("Для замечаний нужен порядок исправлений")
    linked = {ident for f in findings for ident in f["ids"]}
    resolved = {}
    for row in raw["resolved"]:
        _nonempty(row, "reason")
        ident = row["id"]
        if ident not in by_id or ident in resolved or ident in linked:
            raise ValueError(f"Ошибочная или двойная итоговая оценка {ident}")
        resolved[ident] = row["reason"]
    pending = {c["id"] for c in claims if c["status"] != "проверяемо"} - linked - resolved.keys()
    if pending:
        raise ValueError("Нет результата сквозной проверки кандидатов " + ", ".join(sorted(pending)))
    # В свободном тексте тоже нельзя ссылаться на вымышленные ID данного протокола.
    prose = [raw["assessment"], raw["readiness"], *raw["priorities"], *resolved.values()]
    for f in findings:
        prose.extend(f[key] for key in ("topic", "scenario", "consequence", "reason", "question", "test", "fix"))
    for text in prose:
        for ident in re.findall(r"\bR-[\w]+-\d+\b", text):
            if ident not in by_id:
                raise ValueError(f"В тексте вывода указан неизвестный ID {ident}")
    return findings, resolved, {k: raw[k] for k in ("assessment", "readiness", "priorities")}


def _questions(findings):
    questions = {}
    for f in findings:
        if not f["question"]:
            continue
        key = _canon(f["question"])
        if key not in questions:
            questions[key] = {"question": f["question"], "tests": [], "findings": [], "blocking": False}
        q = questions[key]
        q["findings"].append(f["id"])
        if f["test"] not in q["tests"]:
            q["tests"].append(f["test"])
        q["blocking"] |= f["blocking"]
    for q in questions.values():
        q["test"] = " ".join(q.pop("tests"))
    return sorted(questions.values(), key=lambda q: (not q["blocking"], q["findings"]))


def review(document, provider, progress=lambda msg: None):
    blocks = {b.id: b for b in document.blocks}
    if len(blocks) != len(document.blocks) or not blocks:
        raise ValueError("Источник должен содержать блоки с уникальными ID")
    claims, context = [], []
    for number, batch in enumerate(_batches(document.blocks), 1):
        progress(f"Выделение и оценка утверждений: пакет {number}, блоков {len(batch)}.")
        rows, ignored = _local_review(provider, batch, document.blocks, progress)
        claims.extend(rows)
        context.extend(ignored)
    progress(f"Сквозная проверка всего документа: утверждений {len(claims)}.")
    index = [{k: c[k] for k in ("id", "block", "quote", "summary", "assessment", "status")} for c in claims]
    payload = {"blocks": [_source(b) for b in document.blocks], "claims": index}
    findings, resolved, set_review = _request(
        provider, SYNTHESIZE, payload, GLOBAL, lambda data: _set_result(data, claims, blocks), progress)
    for claim in claims:
        links = [f for f in findings if claim["id"] in f["ids"]]
        claim["findings"] = [f["id"] for f in links]
        if claim["id"] in resolved:
            claim["assessment"] = resolved[claim["id"]]
        if any(f["counted"] for f in links):
            claim["status"] = "Выявлено нарушение"
        elif any(f["kind"] == "Предполагаемый пробел" for f in links):
            claim["status"] = "Недостаточно данных"
        elif links:
            claim["status"] = "Есть рекомендация"
        else:
            claim["status"] = "Нарушений не выявлено"
    questions = _questions(findings)
    counts = {"requirements": len(claims), "defects": sum(f["counted"] for f in findings),
              "ambiguities": sum(f["kind"] == "Неоднозначность" for f in findings),
              "gaps": sum(f["kind"] == "Предполагаемый пробел" for f in findings),
              "recommendations": sum(f["kind"] == "Рекомендация" for f in findings),
              "questions": len(questions)}
    return dict(requirements=claims, findings=findings, questions=questions, counts=counts,
                set_review=set_review, context=context)
