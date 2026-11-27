"""Trace changed open coverage rows to the question and test visible to the author."""
import re

from .text import text_key


INSTRUCTION = """
В handoffs перечислены решения матрицы, для которых рецензия изменила вопрос, владельца или статус.
Прочитай исходное обязательство, открытое условие, прежний тест и причину изменения. Сверяй именно
публикуемую группу: у неё один общий вопрос владельца и итоговый текст испытаний. Для каждого key
верни ровно одну запись dispositions. При статусе «покрыто» укажи owner публикуемой группы,
в question_quote скопируй содержательный фрагмент её общего вопроса, в test_quote — фрагмент её
итогового теста. Выбери слова, задающие именно проверяемое условие и наблюдение. Для изменённой
формулировки цитируй её текст после правок. В source_id и source_quote оставь пустые строки.
Если обязательство в действительности уже разрешено или предпосылка неприменима, поставь «закрыто»,
в source_id и source_quote укажи ID утверждения и его дословный фрагмент, а в reason объясни, какое
содержание источника отвечает на это решение или ограничивает его область. Назови предмет строки
и конкретное основание из цитаты, сохраняя терминологию источника. В owner, question_quote
и test_quote оставь пустые строки. Возможность придумать один тест ещё не даёт установленного ответа.
Если решение остаётся открытым, а опубликованный текст его утратил, исправь общий вопрос и тест
или восстанови исходную карточку штатным решением и предъяви исправленные выдержки. Для равнозначных
вопросов достаточно одной группы. Учитывай каждое условие, самостоятельных вопросов сверх ТЗ не добавляй.
"""

_OPEN = {"новое решение", "дополнить", "уже проверено"}
_WORD = re.compile(r"[^\W_]+(?:_[^\W_]+)*", re.UNICODE)
_NOISE = set("""
и или а но в во на с со к ко из от под за по для при до без что как какой какая какие какого каким какую
который которая которое которые кто ли это этот эта эти его ее её мы он она они их всё все такой
and or the an a to of for from at by on in is are it what which how this that its
документ документа документе тз источник источнике источника текст текста вопрос вопроса ответ
решение решения строка строки матрица матрицы карточка карточки требование требования требовании
проверка проверки тест теста указано указан определено определен задано задан покрыто закрыто
уточнено достаточно да нет подтверждено подтверждает следует потому поэтому
""".split())


def _groups(grouped, decisions):
    """The public queue contains contributing IDs but may list the owner after its members."""
    groups = {}
    for group in grouped:
        members = group["findings"]
        owners = [ident for ident in members if not decisions.get(ident, {}).get("same_decision_as")]
        if len(owners) != 1:
            raise ValueError(f"У опубликованного вопроса нужен один прямой владелец: {members}")
        owner = owners[0]
        groups[owner] = dict(owner=owner, question=group["question"], test=group["test"])
    return groups


def _preserved(before, after):
    phrase = text_key(before)
    return bool(phrase) and f" {phrase} " in f" {text_key(after)} "


def build(matrix, raw, findings, grouped, candidates=()):
    """Select only rows whose path to a visible question or its conditions changed."""
    decisions = {d["id"]: d for d in raw["decisions"]}
    accepted = {f["id"]: f for f in findings}
    originals = {f["id"]: f for f in candidates}
    groups = _groups(grouped, decisions)
    handoffs = []
    for row in matrix:
        if row["status"] not in _OPEN:
            continue
        ident = row["finding_id"]
        if not ident or accepted.get(ident, {}).get("missing_target"):
            continue
        current = decisions.get(ident, {})
        owner = current.get("same_decision_as") or ident
        published = groups.get(owner)
        original = originals.get(ident, {})
        previous = dict(question=row.get("question") or original.get("question", ""),
                        test=row.get("test") or original.get("test", ""), outcomes=row.get("outcomes", []))
        if owner != ident:
            transition = "объединён"
        elif current.get("action") == "снять":
            transition = "снят"
        elif not published or not accepted.get(ident, {}).get("question"):
            transition = "нет опубликованного вопроса"
        elif current.get("question_mode") == "заменить" and not all(
                _preserved(previous[key], published[key]) for key in ("question", "test")):
            transition = "условия требуют сверки после замены"
        else:
            continue
        handoffs.append(dict(key=row["key"], finding_id=ident, transition=transition,
                             decision=row["decision"], known=row["known"], distinction=row.get("distinction", ""),
                             checked=row["checked"], previous=previous, published=published,
                             review_reason=current.get("reason", "")))
    return handoffs


def _terms(text):
    return [word for word in _WORD.findall(text.casefold().replace("ё", "е")) if word not in _NOISE]


def _concepts(text):
    # Preserve identifiers and numbers, allow ordinary Russian inflection.
    return {word[:5] if len(word) > 5 and re.fullmatch(r"[а-я]+", word) else word for word in _terms(text)}


def _excerpt(value, text, label, key):
    # Short identifiers may be meaningful in prose, but one isolated word or a
    # verdict such as "задано" cannot establish a condition or an observation.
    if not value.strip() or value != value.strip() or value not in text or len(_terms(value)) < 2:
        raise ValueError(f"{key}: в {label} нужна содержательная дословная выдержка из целевого текста")


def verify(handoffs, dispositions, refreshed_groups, source_quotes, raw_final):
    """Validate witnesses against the actual public group after the normal decision checks."""
    expected = {row["key"]: row for row in handoffs}
    received = {item["key"]: item for item in dispositions}
    if len(received) != len(dispositions) or received.keys() != expected.keys():
        raise ValueError("dispositions: нужен один вердикт по каждому переданному key без чужих или повторных строк")
    decisions = {d["id"]: d for d in raw_final["decisions"]}
    groups = _groups(refreshed_groups, decisions)
    for key, row in expected.items():
        item = received[key]
        previous = row["previous"]
        subject = " ".join((row["decision"], row["known"], row["distinction"], previous["question"],
                            previous["test"], *previous["outcomes"]))
        concepts = _concepts(subject)
        if item["status"] == "покрыто":
            origin = row["finding_id"]
            decision = decisions.get(origin, {})
            # A removed question may already be answered by a surviving group even
            # if adjudication did not record the duplicate. Resolve it explicitly
            # here using the real public text, without adding a question.
            expected_owner = decision.get("same_decision_as") or (origin if origin in groups else "")
            owner = item["owner"]
            if owner not in groups or expected_owner and owner != expected_owner:
                raise ValueError(f"{key}: укажи сохранившийся прямой ID общего вопроса для {origin}")
            if item["source_id"] or item["source_quote"]:
                raise ValueError(f"{key}: открытое решение должно иметь выдержки из опубликованной группы")
            for field in ("question", "test"):
                _excerpt(item[field + "_quote"], groups[owner][field], field + "_quote", key)
            witness = item["question_quote"] + " " + item["test_quote"]
            if concepts and not concepts.intersection(_concepts(witness)):
                raise ValueError(f"{key}: выбери выдержки, в которых виден предмет проверяемого решения")
        elif item["status"] == "закрыто":
            if item["owner"] or item["question_quote"] or item["test_quote"] or item["source_id"] not in source_quotes:
                raise ValueError(f"{key}: для закрытия укажи существующий ID источника и очисти ссылки на вопрос")
            _excerpt(item["source_quote"], source_quotes[item["source_id"]], "source_quote", key)
            reason = item["reason"].strip()
            explanation = _concepts(reason)
            if (len(explanation) < 2 or text_key(reason) == text_key(item["source_quote"])
                    or not explanation.intersection(concepts)
                    or not explanation.intersection(_concepts(item["source_quote"]))):
                raise ValueError(f"{key}: объясни, как фрагмент отвечает на конкретное решение или опровергает его основу")
        else:
            raise ValueError(f"{key}: ожидается статус «покрыто» или «закрыто»")
