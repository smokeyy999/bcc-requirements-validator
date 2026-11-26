"""Check the missing target of a mandatory action against the two proposed test outcomes."""

import re


_TARGET = (r"положени\w*|состояни\w*|режим\w*|значени\w*|статус\w*|метк\w*|меток|цвет\w*|код\w*|"
           r"результат\w*|positions?|states?|modes?|values?|statuses|status|labels?|colou?rs?|codes?|outputs?")
_POINTER = re.compile(
    r"\b(?:указанн\w*|обозначенн\w*|обозначённ\w*|описанн\w*|specified|prescribed|designated)\s+"
    r"(?:(?:здесь|ниже|выше|here|below|above)\s+)?"
    r"(?:(?:[а-яё]+(?:ое|ее|ый|ий|ую|ые|ого)|target|final)\s+){0,2}(?P<target>" + _TARGET + r")\b", re.I)
_ACTION = re.compile(
    r"\b(?:обязан\w*|долж\w*|требуется|следует|must|shall)\b.{0,60}?\b"
    r"(?:перевест\w*|перейт\w*|установ\w*|назнач\w*|присво\w*|помест\w*|перемест\w*|вернут\w*|выдат\w*|"
    r"отобраз\w*|запис\w*|move|switch|enter|set|assign|return|output|display|write)\b", re.I)
_KNOWN = re.compile(r"\b(?:уже|заведомо|признан\w*|распознан\w*|классифицирова\w*|"
                    r"однозначно отнес\w*|already|known|classified)\b", re.I)
_SAME = re.compile(r"\b(?:том же|той же|тех же|одном и том же|same|identical)\b", re.I)
_ELSEWHERE = re.compile(r"\b(?:где|ссылк\w*|адрес\w*|раздел\w*|пункт\w*|како\w* источник|"
                        r"reference|section|where|address|location)\b", re.I)
_MEASURE = re.compile(r"\b(?:срок\w*|задержк\w*|интервал\w*|времени|время|длительност\w*|"
                      r"единиц\w* измерения|latency|duration|deadline|time limit|SLA)\b", re.I)
_OUTPUT_DECISION = re.compile(r"\b(?:целев\w*|конечн\w*|итогов\w*|результир\w*|назнач\w*|присво\w*|"
                              r"верну\w*|после|final|target|expected|returned|assigned|resulting)\b", re.I)
_REFERENCE = re.compile(r"\b(?:пункт\w*|раздел\w*|таблиц\w*|правил\w*|section|rule|table|annex)\s+"
                        r"(?:№\s*)?(?:\w+[-.]\d+|\d+|[A-Z]\b)", re.I)
_EVALUATION = re.compile(r"\b(?:[нН]е\s+)?(?:прохо\w*\s+(?:при[её]мку|проверку|тест)|(?:тест|проверка)\s+"
                         r"(?:проходит|провален\w*)|укладыва\w*\s+в|passes|fails)\b", re.I)
_TOKEN = re.compile(r"«[^»]+»|`[^`]+`|\"[^\"]+\"|[\w-]+")


def _noun_pattern(term):
    # Inflections of the same output noun (e.g. «состояние» and «состоянию»).
    for expr in _TARGET.split("|"):
        if re.fullmatch(expr, term, re.I):
            return re.compile(r"\b(?:" + expr + r")\b", re.I)


def _value_frame(text, noun):
    match = noun.search(text)
    if not match or _EVALUATION.search(text):
        return None
    # Only compare assigned values after a common grammatical subject. Wording
    # changes in the input clause, or different pass/fail criteria, are insufficient.
    tokens = _TOKEN.findall(text[match.end():].casefold())
    if not tokens:
        return None
    return tokens[:-1], tokens[-1]


def _defined(quote, noun):
    return any(re.match(r"\s*(?:[:=—–(]|[-]\s|равн\w*\s|означает\s|is\s|equals\s)\s*"
                        r"[`«\"']?[\w-]+", quote[m.end():], re.I) for m in noun.finditer(quote))


def missing_transition_result(finding, check, source_quotes):
    """The judgement must concern a concrete result on an already fixed input."""
    if (finding["kind"] not in {"Дефект", "Предполагаемый пробел"} or finding.get("reference")
            or finding.get("missing_target") or check["obligation_id"] not in finding["ids"]):
        return False
    rule = source_quotes[check["obligation_id"]]
    decision, outcomes = check["decision"], check["outcomes"]
    if (not _OUTPUT_DECISION.search(decision) or _ELSEWHERE.search(decision) or _MEASURE.search(decision)
            or len(outcomes) != 2):
        return False
    if not _KNOWN.search(" ".join((decision, finding.get("test", ""), *outcomes))):
        return False
    conditions = [s.split(",", 1)[0].strip().casefold() for s in outcomes]
    repeated = "," in outcomes[0] and "," in outcomes[1] and conditions[0] == conditions[1]
    if not repeated and not any(_SAME.search(s) for s in outcomes):
        return False
    for sentence in re.split(r"[.!?;\n]+", rule):
        for pointer in _POINTER.finditer(sentence):
            if not _ACTION.search(sentence[:pointer.start()]) or _REFERENCE.search(sentence[pointer.end():]):
                continue
            noun = _noun_pattern(pointer["target"])
            if not noun.search(decision) or any(_defined(q, noun) for q in source_quotes.values()):
                continue
            first, second = (_value_frame(text, noun) for text in outcomes)
            if first and second and first[0] == second[0] and first[1] != second[1]:
                return True
    return False
