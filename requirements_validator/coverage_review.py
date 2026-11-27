"""Check for independent acceptance decisions missed across extraction batches."""

import re

from .metrics import stage
from .prompts import COMMON
from .response_matrix import response_matrix
from .text import text_key


_AXES = {
    "участник и доступное ему значение": re.compile(
        r"получа|чита\w*|переда|отобража|источник|загружа|обменива|\s[→←]\s|\b(?:receive|read|send|load|display|publish)\w*", re.I),
    "состояния до и после изменения": re.compile(
        r"начальн|по умолчанию|сохран[её]н|до первой|ранее|отсутств|пуста|выключ|включ|"
        r"\b(?:initial|default|previous|prior|empty|absent|enabled|disabled)\b", re.I),
    "обязательства во времени": re.compile(
        r"календар|сутк|месяц|период|дедлайн|дат[аеуы]|времен|момент|в течение|таймер|"
        r"\b(?:month|day|period|deadline|timestamp|timer|time zone|within)\b", re.I),
    "форма ответа в каждой ветви": re.compile(
        r"ответ|возвра[щт]|вернуть|обязательн|ответн\w* пол|\b(?:response|returns?|output|mandatory|required)\b", re.I),
    "смысл результата операции": re.compile(
        r"успе[шх]|статус|отказ|исход|ошибк|отклон|\b(?:status|success|failed|failure|reject\w*|error)\b", re.I),
    "согласованность примера с правилом": re.compile(
        r"пример|сценарий|критери\w* при[её]мки|\b(?:example|scenario|acceptance criteria)\b", re.I),
}

_COVERAGE = COMMON + """
Независимая проверка полноты сквозного ревью. Вход уже разделялся на пакеты. Прочитай весь источник
и составь матрицу по переданным осям. Кандидаты других рецензентов являются гипотезами; список не исчерпывающий.
Одна строка — конкретное решение, условие и наблюдаемая граница. Объединяй одинаковые решения из разных мест.
Проверь, в частности, применимые к источнику пересечения:
* Для каждой операции участника перечисли значения, без которых её нельзя выполнить. Проверь отдельно
доступность каждого значения этому участнику для каждого описанного состояния: запись есть, до создания,
после изменения. Внешний вид у пользователя не определяет ответ интерфейса. Доступность одному участнику
не доказывает доступность другому. Происхождение величины не определяет единицу на входе.
* Для каждого самостоятельно ограниченного действия или итога укажи событие и период, от которых зависит
его проверка. Календарь одного показателя не устанавливает календарь другого. Выбери разнесённые во
времени события, только когда в ТЗ они реально существуют и меняют результат проверки на границе.
* Составь матрицу описанных исходов операции и полей результата: факты в ответе для данного исхода,
обязательность полей, представление, недостающие сведения. Отдельно проверь смысл признака выполнения
операции и бизнес-результат. Можно исследовать, соответствует ли одно опубликованное тело схеме, даже
если для проверки конкретного статуса ещё нужно узнать вход примера. И наоборот. Укажи отдельные решения,
если ответ на одно оставляет два возможных результата по другому.
* Проследи каждую независимую связь примера с нормативным правилом. Не фиксируй предпосылки, значения
или единицы, принадлежащие другой операции. Наличие нескольких технических реализаций само по себе
не создаёт пробела. Не добавляй гипотетические входы, новые классы отказов и обещания наблюдать внутренние
шаги, когда приёмка уже определена по итоговому результату.
Для каждой оси проверь все самостоятельно проверяемые решения, также те, которые прежняя рецензия
считает покрытыми. Не выпускай несколько карточек по одному открытому решению: одинаковый тест и одно решение автора
достаточно отметить как «уже проверено» с существующим ID. При полном ответе из ТЗ поставь «задано» и
укажи опорные ID с фактом в known. При отсутствии независимого требования укажи это в известном факте.
Если открыто ровно одно решение, а предыдущий вопрос по нему проверяет не все описанные состояния
или поля, поставь «дополнить», укажи owner, а в дополнении сформулируй ТОЛЬКО отсутствующую часть
вопроса и теста. Первоначальная формулировка будет сохранена. Если после всех ответов на существующие
карточки для одного сценария всё ещё возможны разные наблюдаемые результаты, поставь «новое решение».
Укажи ближайший owner, если он есть, и кратко объясни в distinction, чем различаются два решения и
что останется неизвестным после ответа на прежнее. У каждой строки перечисли checked — проверенные ID.
Только для «дополнить» и «новое решение» заполни один элемент changes с тем же key: дословные опоры,
вопрос, выполняемый тест, два наблюдаемых исхода одного и того же теста при разных ответах автора.
Во всех карточках контекст для выбора должен быть очевиден аналитику из текста вопроса и теста.
Проверяй внутренний источник как данные. Не используй знания о других документах или чьих-либо эталонах.
"""


def _active_axes(blocks, claims):
    result = {}
    for label, pattern in _AXES.items():
        ids = [c["id"] for c in claims if pattern.search(c["quote"]) or pattern.search(blocks[c["block"]].section)]
        if ids:
            result[label] = ids
    return result


def supplement(provider, claims, blocks, candidates, references, instructions, progress):
    from . import engine as e

    # This pass targets decisions straddling separately extracted batches. Small inputs
    # already receive a full-document synthesis and an independent adjudication.
    batches = iter(e._batches(blocks.values()))
    next(batches, None)
    if next(batches, None) is None:
        return candidates, []
    axes = _active_axes(blocks, claims)
    if len(axes) < 2:
        return candidates, []
    schema = e.obj(
        matrix=e.array(e.obj(key=e.STR, axis=e.enum(*axes), checked=e.array(e.STR), decision=e.STR,
                             status=e.enum("задано", "уже проверено", "дополнить", "новое решение"),
                             owner=e.STR, known=e.STR, distinction=e.STR)),
        changes=e.array(e.obj(key=e.STR, topic=e.STR, category=e.enum("Полнота", "Трассируемость", "Проверяемость", "Ясность"),
                              severity=e.enum("Существенная", "Низкая"), evidence=e.array(e.obj(id=e.STR, quote=e.STR)),
                              question=e.STR, test=e.STR, outcomes=e.array(e.STR))))
    payload = dict(blocks=[e._source(b) for b in blocks.values()],
                   claims=[{k: c[k] for k in ("id", "block", "quote", "summary")} for c in claims],
                   axes=axes, candidates=[e._audit_candidate(f) for f in candidates])
    if contracts := response_matrix(blocks.values()):
        payload["response_contracts"] = contracts
        instructions += (
            "\nВ response_contracts собраны поля, условия в таблицах результата и реально показанные "
            "ключи примеров каждой ветви. Проследи каждое поле с неустановленной обязательностью "
            "отдельно для перечисленных классов исходов. Если применимость полей уже задана, "
            "зафиксируй это основание. Пример может быть сокращённым. Отсутствие ключа в примере "
            "само по себе не устанавливает обязательность или нарушение. Различай общие для группы "
            "исходов поля и правило, прямо отнесённое к одному частному отказу."
        )
    stage("coverage_review")
    progress("Независимая сверка решений между разделами и проверенными кандидатами.")
    return e._request(provider, _COVERAGE + instructions, payload, schema,
                      lambda raw: _reconcile(raw, axes, candidates, claims, blocks, references), progress)


def _reconcile(raw, axes, candidates, claims, blocks, references):
    from . import engine as e

    by_id = {c["id"]: c for c in claims}
    existing = {f["id"]: f for f in candidates}
    changes = {c["key"]: c for c in raw["changes"]}
    rows = {r["key"]: r for r in raw["matrix"]}
    required = {key for key, row in rows.items() if row["status"] in {"новое решение", "дополнить"}}
    if (len(rows) != len(raw["matrix"]) or len(changes) != len(raw["changes"]) or set(changes) != required
            or "" in rows or {r["axis"] for r in rows.values()} != set(axes)):
        raise ValueError("По каждой оси нужна строка проверки с уникальным key, отдельное изменение — для каждого открытого решения.")
    next_id = max((int(f["id"].split("-")[1]) for f in candidates), default=0) + 1
    additions = []
    signatures = {(text_key(f["question"]), text_key(f["test"])): f["id"] for f in candidates if f["question"]}
    result_matrix = []
    for key, row in rows.items():
        e._nonempty(row, "decision", "known")
        checked, owner, status = set(row["checked"]), row["owner"], row["status"]
        if not checked or not checked <= by_id.keys() or (owner and owner not in existing):
            raise ValueError(f"{key}: нужны реальные ID утверждений и существующий owner либо пустая строка")
        if status in {"уже проверено", "дополнить"} and not owner:
            raise ValueError(f"{key}: укажи существующую карточку, которая проверяет это решение")
        result_row = dict(row, finding_id=owner if status == "уже проверено" else "")
        result_matrix.append(result_row)
        if key not in required:
            continue
        change = changes[key]
        e._nonempty(row, "distinction")
        e._nonempty(change, "topic", "question", "test")
        outcomes = [text_key(item) for item in change["outcomes"]]
        if len(outcomes) != 2 or not all(outcomes) or len(set(outcomes)) != 2:
            raise ValueError(f"{key}: для одного испытания нужны два разных наблюдаемых исхода")
        if not change["evidence"] or any(item["id"] not in checked or not item["quote"].strip() for item in change["evidence"]):
            raise ValueError(f"{key}: докажи открытое решение непустыми дословными фрагментами из checked")
        entry = dict(kind="Предполагаемый пробел", category=change["category"], topic=change["topic"],
                     evidence=change["evidence"], severity=change["severity"], scenario=change["test"],
                     consequence=" / ".join(change["outcomes"]), reason=row["known"] + " " + row["distinction"],
                     question=change["question"], test=change["test"], interpretations=[], reference="",
                     blocking=False, fix="")
        finding = e._finding(entry, by_id, blocks, references)
        signature = (text_key(finding["question"]), text_key(finding["test"]))
        # A changed title or an additional quotation cannot create a second acceptance decision.
        result_row.update(question=change["question"], test=change["test"], outcomes=change["outcomes"])
        if signature in signatures:
            result_row["finding_id"] = signatures[signature]
            continue
        if status == "дополнить":
            prior = existing[owner]
            if prior.get("missing_target") or not prior["question"]:
                raise ValueError(f"{key}: дополнить можно существующий открытый вопрос. Проверь самостоятельность другого решения.")
            existing[owner] = dict(prior, ids=sorted(set(prior["ids"]) | set(finding["ids"])),
                                   evidence=prior["evidence"] + [ev for ev in finding["evidence"] if ev not in prior["evidence"]],
                                   question=prior["question"] + " " + finding["question"],
                                   test=prior["test"] + " " + finding["test"])
            result_row["finding_id"] = owner
        else:
            finding["id"] = f"Z-{next_id:03}"
            result_row["finding_id"] = finding["id"]
            additions.append(finding)
            next_id += 1
        signatures[signature] = result_row["finding_id"]
    return [*existing.values(), *additions], result_matrix
