"""Check whether an illustrated HTTP response actually identifies its triggering request."""

import json
import re


_CODE = re.compile(r"(?<![\w.])[1-5]\d{2}(?!\w)")
_STATUS_HEADING = re.compile(r"^(?:HTTP(?:/\d(?:\.\d)?)?\s+)?([1-5]\d{2})\b", re.I)
_RESPONSE = re.compile(r"ответ|response|статус|\bstatus\b|\bHTTP\b", re.I)
_CONDITION = re.compile(r"\b(?:если|когда|при|для|в случае|if|when|with|for)\b", re.I)
_INPUT = re.compile(r"запрос|параметр|вход|значени|request|input|parameter|payload", re.I)
_REQUEST_LINE = re.compile(r"\b(?:curl\b|(?:GET|HEAD|POST|PUT|DELETE|PATCH|OPTIONS)\s+/)", re.I)
_ASSIGNMENT = re.compile(r"\b[\w.-]+\s*=\s*[^\s,;]+")
_REQUEST_LABEL = re.compile(r"^(?:(?:пример|исходный|sample|example)\s+)?(?:запрос\w*|вход\w*|request|input)\b", re.I)
_RESPONSE_LABEL = re.compile(r"^(?:пример\s+)?(?:ответ\w*|response)\b", re.I)
_PRECEDING_OUTPUT = re.compile(
    r"(?:эт\w*|показан\w*|предыдущ\w*|привед[её]нн\w*|данн\w*)\s+(?:выше\s+)?(?:ответ|пример)"
    r"|(?:this|preceding|previous|above)\s+(?:response|example)", re.I)
_STATUS_CHOICE = re.compile(r"(?:выбра\w*|согласован\w*)\s+(?:HTTP[- ]?)?(?:код|статус)|(?:код|статус)\w*\s+на выбор", re.I)
_ASK_INPUT = re.compile(
    r"(?:как\w*|како\w*|каки\w*|чем|что|which|what).{0,55}(?:запрос|параметр|вход|услови|значен|request|input|parameter|condition|value)"
    r"|(?:запрос|параметр|вход|значен|request|input|parameter|value).{0,45}(?:вызыва|воспроиз|соответств|показан|пример|trigger|produce|example)", re.I)
_MESSAGE_FIELDS = {"message", "description", "detail", "errordescription", "errormessage", "сообщение", "описание"}
_TEXT = re.compile(r"текст|сообщени|формулировк|строк[уаие]|литерал|message|literal|wording|text", re.I)
_EXACT = re.compile(r"дословн|в точности|буквальн|фиксированн|точн\w* текст|"
                    r"verbatim|exact(?:ly)?|word.for.word|fixed (?:text|message)", re.I)
_OBLIGATION = re.compile(r"долж|обяза|требу|равен|равна|равно|установи|возвраща|вернуть|"
                         r"\b(?:shall|must|required|return|equals?)\b", re.I)
_EXAMPLE = re.compile(r"образц|из пример|в пример|как в пример|according to the examples?|as (?:shown|illustrated)", re.I)
_ASK_NORM = re.compile(r"(?:обязател\w*|требу\w*|долж\w*|нуж\w*|проверя\w*|входит|норматив\w*)\s+ли|"
                       r"\b(?:is|must|does|should)\b.{0,60}\b(?:required|match|literal|verbatim)\b", re.I)


def _has_request(block, status):
    text = block.text.strip(" *`\n")
    heading = block.section.rsplit(" / ", 1)[-1]
    if _REQUEST_LINE.search(text):
        return True
    if getattr(block, "kind", None) == "code":
        return bool(_REQUEST_LABEL.match(heading))
    if _REQUEST_LABEL.match(text) and (":" in text and text.split(":", 1)[1].strip() or _ASSIGNMENT.search(text)):
        return True
    stated_status = _STATUS_HEADING.match(text)
    return bool(_CONDITION.search(text) and (_INPUT.search(text) or _ASSIGNMENT.search(text)
                or _CODE.search(text) and re.search(r"возвраща|верн[уе]|returns?", text, re.I))
                and (not stated_status or stated_status[1] == status))


def unbound_response_examples(blocks):
    """Identify output bodies under status headings, retaining the nearest example's own context."""
    examples = {}
    for i, block in enumerate(blocks):
        if getattr(block, "kind", None) != "code":
            continue
        section = block.section.split(" / ")
        status = next((m[1] for title in reversed(section) if (m := _STATUS_HEADING.match(title))), "")
        if not status or _REQUEST_LABEL.match(section[-1]) or _REQUEST_LINE.search(block.text):
            continue
        if _CONDITION.search(section[-1]) and _INPUT.search(section[-1]):
            continue
        if i + 1 < len(blocks):
            after = blocks[i + 1]
            if (after.section == block.section and _PRECEDING_OUTPUT.search(after.text)
                    and (_REQUEST_LINE.search(after.text) or _ASSIGNMENT.search(after.text)
                         or _has_request(after, status))):
                continue
        # Adjacent request and response may be subheadings of the same scenario.
        path = list(section)
        while path and (_STATUS_HEADING.match(path[-1]) or _RESPONSE_LABEL.match(path[-1])):
            path.pop()
        has_request = False
        alternative = False
        for j in range(i - 1, -1, -1):
            prev = blocks[j]
            same_section = prev.section == block.section
            previous = prev.section.split(" / ")
            request_section = _REQUEST_LABEL.match(previous[-1]) and previous[:-1] == path
            if not same_section and not request_section:
                break
            if _has_request(prev, status):
                has_request = True
                break
            if getattr(prev, "kind", None) == "code" and not alternative:
                break
            alternative = prev.text.strip().casefold() in {"или", "or"}
        if not has_request:
            examples[block.id] = status
    return examples


def _descriptive_literal(quote):
    fenced = re.fullmatch(r"```(?:json)?\s*\n(.*)\n```", quote.strip(), re.I | re.S)
    try:
        body = json.loads(fenced[1] if fenced else quote)
    except (ValueError, TypeError):
        return ""
    if not isinstance(body, dict) or len(body) != 1:
        return ""
    name, value = next(iter(body.items()))
    return value if name.casefold().replace("_", "") in _MESSAGE_FIELDS and isinstance(value, str) else ""


def _message_example_error(finding, evidence, unbound, outputs, rule_codes, source_quotes):
    if not finding or finding.get("counted") or len(outputs) != 1 or outputs != rule_codes:
        return ""
    question = finding.get("question", "")
    if not _ASK_INPUT.search(question) or (_ASK_NORM.search(question) and _TEXT.search(question)):
        return ""
    literals = {_descriptive_literal(e["quote"]) for e in evidence if e.get("block") in unbound}
    if len(literals) != 1 or "" in literals:
        return ""
    literal = literals.pop()
    observations = " ".join((question, finding.get("test", ""), *finding.get("question_basis", {}).get("outcomes", [])))
    if literal.casefold() not in observations.casefold() and not (_EXACT.search(observations) and _TEXT.search(observations)):
        return ""
    for quote in source_quotes:
        if _OBLIGATION.search(quote) and (literal.casefold() in quote.casefold() or
                (_EXACT.search(quote) and _TEXT.search(quote) and _EXAMPLE.search(quote))):
            return ""
    return ("Класс входов и статус уже связаны правилом. Иллюстрация содержит только описательное "
            "сообщение. Выбери action=снять, если отдельное сомнение касается лишь поиска запроса "
            "для точного текста образца. Сохраняй вопрос о дословной проверке только при наличии "
            "самостоятельного основания в источнике. Сначала уточни обязательность литерала; "
            "отдельный вход требуется лишь при подтверждении автором.")


def input_scope_error(finding, original, unbound, source_quotes=None):
    if not unbound:
        return ""
    evidence = original["evidence"]
    options = {item["anchor"]["id"] for item in original.get("proposal_options", [])}
    if not options and (original.get("counted") or not original.get("question")):
        return ""
    outputs = {unbound[e["block"]] for e in evidence if e.get("block") in unbound and (not options or e["id"] in options)}
    if not outputs:
        return ""
    rule_codes = set()
    for e in evidence:
        if options and e["id"] not in options:
            continue
        quote = e["quote"]
        if _INPUT.search(quote) and _CONDITION.search(quote) and _RESPONSE.search(quote):
            rule_codes.update(_CODE.findall(quote))
    text = " ".join(original.get(key, "") for key in ("topic", "question", "test", "consequence", "reason"))
    rules = (rule_codes - outputs) & set(_CODE.findall(text))
    if not rules or not outputs.intersection(_CODE.findall(text)):
        quotes = source_quotes.values() if source_quotes is not None else (e["quote"] for e in evidence)
        return _message_example_error(finding, evidence, unbound, outputs, rule_codes, quotes)
    if (finding and not finding["counted"] and _ASK_INPUT.search(finding["question"])
            and rules.intersection(_CODE.findall(finding["test"])) and not _STATUS_CHOICE.search(finding["test"])):
        return ""
    return ("Пример содержит только ответ. Сохрани самостоятельный вопрос о конкретном запросе, его параметрах "
            "или входном условии, которое воспроизводит этот пример. Не предлагай выбирать иной статус для уже "
            "определённого класса входов. В зависимом тесте отдельно проверь установленный правилом статус "
            + "/".join(sorted(rules)) + " и лишь по ответу автора воспроизведи пример для указанного входа. "
            "При совпадении условий объясни возможное расхождение условно.")


EXAMPLE_SCOPE_INSTRUCTION = """
Для перечисленных response_examples_without_request источник показывает тело ответа под статусом без
входа соответствующего примера. Сообщение в теле, соседний успешный запрос в другом примере и самостоятельно
подобранное граничное значение не устанавливают, какой запрос дал этот ответ. Если ставишь под вопрос
правило для определённого входа, сопоставь обе стороны: какая дословная строка привязывает именно этот
пример к тому же запросу? При наличии явной привязки сохрани реальный конфликт. Если правило установлено,
а его применимость к примеру неизвестна, оставь отдельный вопрос: какой конкретный запрос, набор параметров
или класс входов воспроизводит показанный ответ? В зависимом тесте сначала проверь прямо установленный
статус для входа из правила; отдельно, после ответа автора, воспроизведи пример с его исходным запросом.
Не предлагай выбрать между статусами до установления общего входа. Общие расхождения схемы, типов
и формата можно проверять независимо от примеров входа, когда контракт прямо распространяется на любой ответ.
Одиночный пример обычного сообщения об ошибке может иллюстрировать уже заданный класс ответа.
Прежде чем требовать отдельный вход для воспроизведения дословного текста, найди требование
о точном литерале, противоречащий исход или иную проверку, которая изменится от ответа автора.
Образец произвольного описательного сообщения сам по себе не устанавливает обязательный текст.
Если в общей таблице есть ветка статуса, а правила этого метода уже определяют другие коды
для конкретных отказов, сначала спроси, применима ли общая ветка к этому методу. Лишь при
положительном ответе запрашивай отличающееся условие; сохрани установленные коды в тесте.
"""
