"""Separate the amount of a full reversal from the scope of partial reversals."""

import re


_REFUND = re.compile(r"\b(?:возврат\w*|возмещени\w*|сторн\w*|refund\w*|reversals?)\b", re.I)
_TOTAL = re.compile(r"расход\w*|оборот\w*|затрат\w*|траты|spending|expenses?|expenditure|turnover", re.I)
_DECREASE = re.compile(r"уменьш\w*|снижа\w*|вычит\w*|сокращ\w*|deduct\w*|decreas\w*|reduc\w*|subtract\w*", re.I)
_NEGATED_DECREASE = re.compile(r"(?:не\s+|not\s+)(?:" + _DECREASE.pattern + ")", re.I)
_PART = re.compile(r"\b(?:частич\w*|част[ьи]\s+сумм\w*|partial\w*|part of the amount)\b", re.I)
_FULL = re.compile(r"\b(?:полн\w*|целиком|full\w*|in full)\b", re.I)
_VALUE = re.compile(r"сумм\w*|величин\w*|размер\w*|сколько|расч[её]т\w*|вычисл\w*|amount|how much|calculat\w*", re.I)
_ASK_AMOUNT = re.compile(
    r"на\s+(?:сколько|какую\s+(?:сумму|величину))|как\w*\s+(?:сумм\w*|величин\w*|размер\w*|"
    r"вычисл\w*|рассчит\w*|определ\w*|пересчит\w*)|по какому правилу\s+(?:рассчит\w*|уменьш\w*)|"
    r"how much|what amount|how (?:is|to) .{0,40}calculat", re.I)
_SCOPE = re.compile(
    r"(?:вход\w*|охват\w*|распространя\w*|примен\w*|допуска\w*|разреш\w*|поддерж\w*|возмож\w*|"
    r"можно|обязан\w*|предусм\w*|включ\w*|учитыва\w*|обрабатыва\w*|относ\w*|требуется|долж\w*|"
    r"нуж\w*|следует|покрыва\w*)\s+ли\b|только\s+полн\w*[^?]{0,50}\sили\s|"
    r"\b(?:does|do|is|are|should|can)\b[^?]{0,80}\b(?:scope|cover\w*|support\w*|include\w*|allow\w*|apply)\b", re.I)
_SPECIAL = re.compile(
    r"комисси\w*|удержан\w*|сбор\w*|процент\w*|конверт\w*|курс\w* валют\w*|округл\w*|"
    r"коэффициент\w*|за вычетом|(?:по|согласно) формул\w*|\d\s*%|\bfee\w*|exchange rate|"
    r"conversion|deductible|rounding|coefficient|withhold\w*|according to (?:a |the )?formula", re.I)
_UNSPECIFIED_AMOUNT = re.compile(
    r"(?:друг\w*|ин(?:ая|ую|ой|ом|ое|ого|ые|ом))\s+(?:величин\w*|сумм\w*|значен\w*|размер\w*)|"
    r"(?:сумм\w*|величин\w*)\s+(?:может\s+)?отлича\w*|another amount|different amount", re.I)
_SPECIFIED_COVERAGE = re.compile(
    r"(?:только|исключительно)\s+полн\w*\s+(?:возврат|сторн)|only full (?:refund|reversal)|"
    r"(?:частич\w*\s+(?:возврат\w*|сторн\w*)|partial (?:refunds?|reversals?))\s+"
    r"(?:(?:are|is|не|not)\s+)*(?:разреш\w*|поддерж\w*|запрещ\w*|предусмотр\w*|"
    r"допуска\w*|allowed|permitted|supported|excluded)|"
    r"(?:разреш\w*|допуска\w*|запрещ\w*|поддержива\w*)\s+частич\w*\s+(?:возврат|сторн)", re.I)


def _reduces_spending(text):
    return bool(_REFUND.search(text) and _DECREASE.search(text) and _TOTAL.search(text)
                and not _NEGATED_DECREASE.search(text))


def refund_rules(claims):
    return [claim["id"] for claim in claims if _reduces_spending(claim["quote"])]


def refund_scope_error(finding, original, source_quotes):
    if not finding or not finding.get("question"):
        return ""
    question = finding["question"]
    if not _REFUND.search(question) or not (_PART.search(question) or _VALUE.search(question)):
        return ""
    basis = finding.get("question_basis", {})
    ids = set(finding["ids"]) | set(basis.get("checked_ids", []))
    quotes = [source_quotes[i] for i in ids if i in source_quotes]
    if not any(_reduces_spending(q) for q in quotes):
        return ""
    # A fee or exchange rule on a different operation does not change this reversal.
    related = [q for q in quotes if _REFUND.search(q)]
    if any(_SPECIAL.search(q) for q in related):
        return ""
    if any(_SPECIFIED_COVERAGE.search(q) for q in related):
        if _PART.search(question) and _SCOPE.search(question):
            return ("Применимость частичного возврата прямо задана. Сохрани установленный ответ "
                    "и уточни лишь независимое открытое решение, если оно есть.")
        return ""
    # Questions about the booking period, link to the original, duplicate events, etc. stay independent.
    original_question = original.get("question", "")
    amount_case = (_ASK_AMOUNT.search(question) or _SCOPE.search(question) and _PART.search(question)
                   or _PART.search(question) and _FULL.search(question) and _VALUE.search(original_question))
    if not amount_case:
        return ""
    outcomes = basis.get("outcomes", [])
    full_control = _FULL.search(finding.get("test", "")) or any(_FULL.search(text) for text in outcomes)
    arbitrary_full = full_control and any(
        _UNSPECIFIED_AMOUNT.search(text) and not _PART.search(text) for text in outcomes)
    if not _PART.search(question) or not _SCOPE.search(question) or arbitrary_full:
        return ("Уточни только границу применимости частичного возврата и списание фактически "
                "возвращённой части после её подтверждения. Полный возврат оставь контрольным "
                "примером: уменьшение равно сумме исходной покупки. Сравни два исхода только "
                "для частичного возврата. Иной размер при полном возврате требует отдельного "
                "основания об удержании, пересчёте или другой корректировке именно этой операции.")
    return ""


REFUND_INSTRUCTION = """
Для refund_rules отдели полный возврат расходной операции от возможности вернуть её часть.
Если покупка учтена по своей сумме, а возврат уменьшает расходы исходной покупки, полный возврат
проверяй как снятие всей этой суммы в исходном периоде. Сначала сверь источник: комиссия, валюта,
округление или иная явно заданная корректировка именно этой операции могут изменить расчёт.
Без такой опоры не предлагай второй произвольный размер для полного возврата.
Если применение того же правила к части суммы открыто, сформулируй узкий вопрос владельцу:
распространяется ли правило на частичный возврат, и если да, уменьшается ли итог на фактически
возвращённую часть? Для одного частичного возврата покажи два исхода по решению о его применимости.
В тесте оставь полный возврат в качестве контроля, затем отдельно проверь частичный по ответу автора.
Явно согласованные условия сохрани. Не задавай вопрос, на который документ уже отвечает.
"""
