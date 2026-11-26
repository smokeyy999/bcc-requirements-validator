"""Source-local review leads. A lead is a request to compare evidence, not a verdict."""

from collections import defaultdict
from fractions import Fraction
import re


# Factors within each dimension use one exact common scale.
_UNITS = (
    ("ms", 1, r"миллисекунд\w*|milliseconds?|ms|мс"),
    ("ms", 1000, r"секунд\w*|seconds?|sec|s|сек|с"),
    ("ms", 60000, r"минут\w*|minutes?|min|мин"),
    ("ms", 3600000, r"час(?:а|ов|ах|ами|ы)?|hours?|hrs?|h|ч"),
    ("ms", 86400000, r"сут(?:ки|ках|ок|кам|ками)|дн(?:ей|ях|я|и)|день|days?"),
    ("mm", 1, r"миллиметр\w*|millimet(?:er|re)s?|mm|мм"),
    ("mm", 10, r"сантиметр\w*|centimet(?:er|re)s?|cm|см"),
    ("mm", 1000, r"метр(?:ы|ов|ах|а|ами)?|met(?:er|re)s?|m|м"),
    ("mg", 1, r"миллиграмм\w*|milligrams?|mg|мг"),
    ("mg", 1000, r"грамм\w*|grams?|g|г"),
    ("mg", 1000000, r"килограмм\w*|kilograms?|kg|кг"),
)
_UNIT = "(?:" + "|".join(pattern for _, _, pattern in _UNITS) + r")(?!\w)"
_WORDS = {}
for words in ("ноль один два три четыре пять шесть семь восемь девять десять одиннадцать двенадцать тринадцать четырнадцать пятнадцать шестнадцать семнадцать восемнадцать девятнадцать",
              "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen"):
    _WORDS.update({word: value for value, word in enumerate(words.split())})
_WORDS.update({"одна": 1, "одно": 1, "две": 2})
_NUMBER = r"(?:[+-]?\d{1,12}(?:[.,]\d{1,9})?|" + "|".join(_WORDS) + r")"
_DECLARATION = re.compile(
    r"\b(?:зада[её]тся|указывается|измеряется|выражается|задан[аоы]?|указан[аоы]?|выражен[аоы]?|"
    r"измерен[аоы]?|specified|expressed|measured|given)\s+(?:в|in)\s+(?P<unit>" + _UNIT + ")", re.I)
_INTERPRETATION = re.compile(
    r"\s*[,;:.—-]?\s*(?:значени[ея]|число|числу|a value of|the value|value|input)?\s*"
    r"(?P<input>" + _NUMBER + r")\s*(?:означа(?:ет|ют)|соответству(?:ет|ют)|эквивалентно|"
    r"means|represents|maps to|corresponds to|is equivalent to|=|→)\s*"
    r"(?P<output>" + _NUMBER + r")\s*(?P<unit>" + _UNIT + ")", re.I)
_EXCEPTION = re.compile(r"\b(?:исключени\w*|кроме|иначе|умолчанию|приоритет\w*|"
                        r"except\w*|unless|override\w*|default)\b", re.I)
_ACCEPTANCE = re.compile(r"\b(?:при[её]м\w*|тест(?:ы|а|ов|ирование|ирования)?|"
                         r"acceptance|test(?:s|ing)?)\b", re.I)
_DEFERRED = re.compile(r"\b(?:(?:опиш\w*|описа\w*|уточн\w*|добав\w*|определ\w*)\s+(?:позже|позднее)|"
                       r"предстоит\s+(?:описать|добавить|определить)|"
                       r"(?:буд\w+|планируется)\s+(?:уточн\w+|добав\w+|опис\w+|соглас\w+|определ\w+|состав\w+|подготов\w+)|"
                       r"не\s+(?:определен\w*|определён\w*|заданы?|описан\w*)|"
                       r"to be (?:defined|specified|added)|tbd|todo)\b", re.I)


def _measure(unit):
    return next((base, scale) for base, scale, pattern in _UNITS if re.fullmatch(pattern, unit, re.I))


def _number(token):
    value = _WORDS.get(token.casefold())
    return Fraction(value) if value is not None else Fraction(token.replace(",", "."))


def _covering_ids(rows, *phrases):
    """Prefer the smallest extracted quote containing each exact source phrase."""
    result = []
    for phrase in phrases:
        matches = [row for row in rows if phrase in row["quote"]]
        if not matches:
            return []
        ident = min(matches, key=lambda row: len(row["quote"]))["id"]
        if ident not in result:
            result.append(ident)
    return result


def source_signals(blocks, claims):
    grouped = defaultdict(list)
    for claim in claims:
        grouped[claim["block"]].append(claim)
    signals = []
    for block in blocks:
        rows = grouped[block.id]
        for rule in _DECLARATION.finditer(block.text):
            case = _INTERPRETATION.match(block.text, rule.end())
            if not case:
                continue
            base, declared_scale = _measure(rule["unit"])
            outcome_base, example_scale = _measure(case["unit"])
            expected = _number(case["input"]) * declared_scale
            observed = _number(case["output"]) * example_scale
            if base != outcome_base or expected == observed:
                continue
            signals.append({"type": "unit_scale", "block": block.id,
                            "claims": _covering_ids(rows, rule.group(), block.text[case.start("output"):case.end("unit")]),
                            "source": block.text[rule.start():case.end()], "base_unit": base,
                            "by_declaration": str(expected), "by_example": str(observed),
                            "qualified": bool(_EXCEPTION.search(block.text))})
        deferred = _DEFERRED.search(block.text)
        if deferred and (_ACCEPTANCE.search(block.text) or _ACCEPTANCE.search(block.section)):
            signals.append({"type": "deferred_acceptance", "block": block.id,
                            "claims": _covering_ids(rows, deferred.group()), "marker": deferred.group()})
    return signals


def grouped_in(signal, findings):
    ids = set(signal["claims"])
    return bool(ids) and any(ids.issubset(f["ids"]) for f in findings)


def has_support(signal, supports):
    """Repeating contradictory measurements is insufficient evidence of an exception."""
    if not supports:
        return False
    return (signal["type"] != "unit_scale" or signal["qualified"]
            or bool(set(supports) - set(signal["claims"])))


SIGNAL_INSTRUCTION = (
    "Для каждого source_signal сравни указываемые ID. Зафиксируй общий предмет, условие и результат. "
    "В unit_scale обе величины уже приведены к base_unit. Числовой пример сам по себе не вводит "
    "новый масштаб: для исключения нужно отдельное основание в тексте. В deferred_acceptance "
    "проверь по всему документу, заданы ли недостающие шаг и ожидаемый результат для указанного "
    "сценария. Сам факт отложенного описания не меняет функциональное поведение. Если конкретное "
    "содержание приёмки обещано, но отсутствует, проверь полноту этого содержания. "
    "Сигнал не предрешает вывод. В сквозной проверке дай общую карточку с указанными ID либо "
    "предметное объяснение в resolved с supports для каждого ID. Рецензенту для снятия "
    "расхождения шкал нужны дословные основания исключения или другого предмета сравнения."
)
