"""Distinguish acceptance of a measured interval from instrumentation of its substeps."""

from collections import defaultdict
import re


def _pattern(text):
    return re.compile(text, re.I)


_CLOCK = _pattern(r"таймер|секундомер|измеря\w*|timer|stopwatch|measur\w*")
_SPAN = _pattern(r"\b(?:от|с момента)\s+[а-яё][^.!?;]{1,110}\s+до\s+[а-яё]|"
                 r"\bfrom\s+[a-z][^.!?;]{1,110}\s+(?:to|until)\s+[a-z]")
_WHOLE = _pattern(r"\b(?:полн\w*|всего|общ\w*)\s+(?:цикл\w*|интервал\w*|врем\w*|процесс\w*|операци\w*)|"
                  r"\b(?:full|whole|complete|total)\s+(?:cycle|interval|operation|time|duration)|end.to.end")
_ACCEPT = _pattern(r"при[её]м\w*|acceptance|pass(?:es)?\s+if")
_LIMIT = _pattern(r"(?:не более|не дольше|не позднее|не превыша\w*|максимум|до|at most|no (?:more|longer) than|"
                  r"within|<=|≤)\s*\d+(?:[.,]\d+)?\s*(?:мс|мкс|миллисекунд\w*|секунд\w*|минут\w*|"
                  r"ms|milliseconds?|seconds?|minutes?)\b")
_LINKED_EVENTS = _pattern(r"в момент|одновременн\w*|без задержки|синхронно|"
                          r"at the (?:same time|moment)|simultaneous\w*|without delay")
_SEPARATE_TEST = _pattern(r"(?:отдельно|независимо|поэтапно)\s+[^.!?;]{0,55}(?:измер|провер|фиксир|контрол|принима)|"
                          r"(?:измер|провер|фиксир|контрол)\w*\s+[^.!?;]{0,45}(?:отдельно|поэтапно)|"
                          r"(?:для каждого|для отдельного)\s+этапа|(?:точность синхронизации|допуск (?:совпадения|рассинхронизации))|"
                          r"(?:separately|independently)\s+(?:measur|test|verif)|(?:measur|test|verif)\w*\s+[^.!?;]{0,40}separately|"
                          r"(?:per.stage|for each stage|synchroni[sz]ation tolerance)")
_METROLOGY = _pattern(r"наблюден|наблюдаем|наблюдать|точност|погрешност|допуск|разрешени\w*\s+(?:шкал|таймер)|"
                      r"критери|каки\w*\s+(?:приб|способ)|как\s+(?:измер|провери|подтверд|зафиксир)|от какого (?:момента|события)|"
                      r"precision|accuracy|tolerance|observ\w*|how (?:to|should|can)\s+(?:measure|verify|confirm)")
_SUBSTEP = _pattern(r"совпад\w*|одновременн\w*|синхрон\w*|без задержки|отсутстви\w* задержки|промежуточн\w*|"
                    r"(?:задержк\w*|срок\w*)\s+(?:отправк|передач|регистрац|фиксац)|кажд\w+\s+этап\w*|"
                    r"substep|intermediate|per.stage|simultaneous\w*|coinciden\w*|without delay|synchron\w*")
_STAGE_TIME = _pattern(r"(?:врем\w*|длительност\w*|задержк\w*|срок\w*)\s+(?:этап\w*|передач\w*|"
                       r"отправк\w*|регистраци\w*|обработк\w*|фиксаци\w*)|"
                       r"(?:processing|registration|transmission|stage)\s+(?:latency|time|duration)")
_OBLIGATION = _pattern(r"долж\w*|требу\w*|при[её]м\w*|обяз\w*|must|shall|required|acceptance")


def _has_stage_test(text):
    for clause in re.split(r"[.!?;\n]", text):
        if (_SEPARATE_TEST.search(clause) or (_METROLOGY.search(clause) and _ACCEPT.search(clause)
                and _SUBSTEP.search(clause))):
            return True
        if _STAGE_TIME.search(clause) and (_LIMIT.search(clause) or _OBLIGATION.search(clause)):
            return True
    return False


def _mentions_rule(text, row):
    return row.source_id and re.search(rf"(?<![\w-]){re.escape(row.source_id)}(?![\w-])", text, re.I)


def measurement_scopes(blocks, claims):
    """Pair a documented start/stop with acceptance of the same complete operation."""
    sections, by_block = defaultdict(list), defaultdict(list)
    for block in blocks:
        sections[block.section].append(block)
    for claim in claims:
        by_block[claim["block"]].append(claim)

    def ids(rows):
        return [claim["id"] for row in rows for claim in by_block[row.id]]

    # An explicit test in a different section can impose an additional obligation.
    separate = [block for block in blocks if _has_stage_test(block.text)]
    scopes = []
    for rows in sections.values():
        intervals = [row for row in rows if _CLOCK.search(row.text) and _SPAN.search(row.text)]
        for rule in rows:
            if not (_WHOLE.search(rule.text) and _ACCEPT.search(rule.text)):
                continue
            linked = [row for row in intervals if _mentions_rule(rule.text, row)]
            candidates = linked or intervals
            if len(candidates) != 1:
                continue
            interval = candidates[0]
            stage_rows = [row for row in rows if row.id == interval.id or _mentions_rule(row.text, interval)]
            stages = [claim["id"] for row in stage_rows for claim in by_block[row.id]
                      if _LINKED_EVENTS.search(claim["quote"])]
            if not stages or not by_block[rule.id] or not by_block[interval.id]:
                continue
            scopes.append(dict(interval_ids=ids([interval]), acceptance_ids=ids([rule]),
                               linked_event_ids=stages, separate_test_ids=ids(separate),
                               numeric_limit=bool(_LIMIT.search(rule.text))))
    return scopes


def scope_error(finding, scopes):
    if not finding or not finding.get("question") or not _METROLOGY.search(finding["question"]):
        return ""
    if not _SUBSTEP.search(finding["question"]):
        return ""
    for scope in scopes:
        if (scope["numeric_limit"] and not scope["separate_test_ids"]
                and set(finding["ids"]).intersection(scope["linked_event_ids"])):
            return ("Для полного интервала уже заданы начало, конец и численный критерий. "
                    "Вопрос запрашивает дополнительный способ или точность наблюдения промежуточных событий. "
                    "Сними карточку с указанием оснований. Для отдельного критерия этапа требуются "
                    "самостоятельное обязательство в источнике и иной приёмочный результат.")
    return ""


INSTRUCTION = (
    "В measurement_scopes указаны события измерения и критерий приёмки полного интервала. "
    "Подтверди предварительные признаки по исходным блокам. Установи, что именно показывает заданный прибор, по какому пределу "
    "принимается его показание и есть ли отдельное обязательство проверять внутренний этап. "
    "Указанная синхронность событий задаёт их порядок или связь. Дополнительная шкала точности, "
    "задержка передачи сигнала и инструмент наблюдения требуют собственного основания в тексте. "
    "Когда полный цикл уже однозначно измеряется и принимается по численному пределу, "
    "сними самостоятельный вопрос о том, чем или с какой точностью наблюдать промежуточные события, "
    "если автор не требует отдельного результата для них. В resolved/обосновании укажи известный "
    "способ проверки. Если для полного цикла задано лишь качественное ожидание, сохрани вопрос "
    "о допустимом значении и граничном результате этого цикла. Если требуется самостоятельная "
    "проверка промежуточного этапа, сохрани её и свяжи с конкретной цитатой.")
