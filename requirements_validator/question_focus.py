"""Check concrete semantic mistakes in the question and its published evidence."""

import re


FOCUS_INSTRUCTION = """
Проверяй начальные значения каждого поля по отдельности. Значение одного флага по умолчанию
не задаёт значение соседнего поля и момент создания записи. Для незаданного значения сначала
спроси, каким оно должно быть. В тесте ответа можно явно подготовить конкретное прежнее
состояние, сохраняя его статус тестового предусловия.
Сравни два результата одного публичного действия. Если выбран тот же объект и в оба запроса
поступает тот же идентификатор, различие внутренних путей получения само по себе не требует
решения автора ТЗ. Оставь вопрос, когда меняются наблюдаемые данные, участник, права или
обязательный внешний обмен. Обоснуй такое различие цитатой.
Для чтения разделяй независимые решения о начальном значении и контракте обмена. Краткий
вопрос о контракте определяет запрос и поля ответа; чтение сохранённых значений и повторное
чтение после замены проверь в тесте. Состояние до первой записи требует своего решения,
если его нельзя вывести из того же ответа. Выдели разные решения при построении кандидатов.
"""


_INITIAL = re.compile(r"до перв\w+ (?:сохран|запис|измен|настрой)\w*|по умолчанию|"
                      r"при (?:создании|выпуске|инициализации)|изначально|начальн\w+ состоян", re.I)
_SENTENCE_END = re.compile(r"[!?;\n]|(?<!\d)\.|\.(?!\d)")
_UNCERTAIN = re.compile(r"\b(?:если|допустим|предположим|неизвестно|неясно|ли)\b|"
                        r"не (?:указывает|определяет|устанавливает|следует|указано|определено),? "
                        r"(?:есть|что|существует)|(?:не подтвержден|не доказан|не установлен)\w* "
                        r"(?:исходник|источник|текст|документ)", re.I)
_FIXTURE = re.compile(r"(?:для|взять|выбрать|подготовить) [^.;?!]{1,75}\bбез "
                      r"(?:записи|настройки|сохран[её]нн\w+ значени)|"
                      r"\b(?:тестов\w+ предуслови|для (?:этого )?теста|тестов\w+ данн)", re.I)
# Retain the noun for the absent property: an explicitly absent different
# field is not evidence. Only affirmative, initial-state statements are tested.
_WORD = r"[^\W\d][\w-]*"
_OPTIONAL_MODIFIER = r"(?:(?:сохран[её]нн|заданн|начальн|исходн)\w+\s+)?"
_ABSENCE = re.compile(
    r"\b(?:отсутству(?:ет|ют)|отсутстви[ея]|нет)\s+" + _OPTIONAL_MODIFIER + r"(?P<after>" + _WORD + r")"
    r"|\b(?P<before>" + _WORD + r")\s+(?:нет\b|отсутству(?:ет|ют)\b|не (?:задан|назначен|установлен)[аоы]?\b"
    r"|(?:равен|равно|равна|=)\s*null\b)", re.I)
_NUMERIC_DEFAULT = re.compile(
    r"(?:@\s*(?:значени[ея]\s+)?(?P<after>" + _WORD + r")|(?P<before>" + _WORD + r")\s*@)"
    r"\s*(?:[:=—–]|равен|равно|равна|составляет)?\s*"
    r"(?P<value>[+-]?\d+(?:[ \u00a0\u202f]\d{3})*(?:[.,]\d+)?)\b", re.I)


def _default_claims(text):
    # Compare the same property and the same value, not just a mention of a
    # number (e.g. a permitted lower bound) somewhere in the cited source.
    claims = set()
    for pattern, sentence in ((_ABSENCE, text), (_NUMERIC_DEFAULT, _INITIAL.sub("@", text))):
        for match in pattern.finditer(sentence):
            term = match["after"] or match["before"]
            stem = re.sub(r"(?:иями|ами|ями|ого|его|ов|ев|а|я|и|ы|е|у|ю|ь)$", "", term.casefold())
            value = match.groupdict().get("value") or "отсутствует"
            claims.add((stem, "".join(value.split()).replace(",", ".")))
    return claims


def _initial_error(finding, basis, quotes):
    supported = set()
    for quote in quotes:
        for sentence in _SENTENCE_END.split(quote):
            if _INITIAL.search(sentence) and not _UNCERTAIN.search(sentence):
                supported.update(_default_claims(sentence))
    facts = [basis.get("known_answer", ""), finding.get("reason", ""), finding.get("consequence", "")]
    # A question about representation can itself presuppose an empty initial
    # value. An explicit choice between empty and set is a legitimate question.
    for question in (finding.get("question", ""), basis.get("decision", "")):
        if not re.search(r"\b(?:или|либо)\b", question, re.I):
            facts.append(question)
    for field in facts:
        for sentence in _SENTENCE_END.split(field):
            if _INITIAL.search(sentence) and not _UNCERTAIN.search(sentence) and not _FIXTURE.search(sentence):
                if _default_claims(sentence) - supported:
                    return ("Начальное значение или отсутствие поля заявлено как факт. Укажи в checked_ids "
                            "прямое требование об этом же поле и значении при инициализации. Если определён только "
                            "соседний признак, оставь значение открытым и спроси о нём. Конкретное состояние "
                            "для проверки ответа задай как подготовленное предусловие теста.")
    return ""


_ID = re.compile(r"\b(?:[A-Za-z_][A-Za-z0-9_]*(?:Id|ID|_id)|(?i:ID|идентификатор[а-яё]*))\b")
_ORIGIN = re.compile(r"откуда|источник|откуда брать|как [^?]{0,70}(?:получ|прослед)", re.I)
_ROUTE_TAIL = re.compile(r"^\s*,?\s*(?:из\b|через\b|полученн\w*\b|взят\w*\b)", re.I)
_EXTERNAL = re.compile(r"\b(?:HTTP|GET|POST|PUT|PATCH|JWT)\b|/[\w-]+/|"
                       r"заголов\w*|токен\w*|подпис\w*|авторизац\w*|прав[ао]\s+доступа|"
                       r"друг(?:ой|ого|ому) (?:объект|карт|устройств|клиент)|чуж\w+|отклон\w*|"
                       r"обязател\w* (?:вызов|запрос|обмен)|долж\w* (?:получать|брать|запрашивать) из", re.I)
_MANDATED_ORIGIN = re.compile(r"(?:бер[её]тся|читается|извлекается|получает(?:ся)?|"
                              r"долж\w* (?:получать|брать|считывать))\s+(?:только |строго )?из\b|"
                              r"источник(?:ом)?\s+(?:идентификатора|[\w-]*id)\b", re.I)


def _sent_id(outcome):
    for ident in _ID.finditer(outcome):
        prefix, tail = outcome[:ident.end()], outcome[ident.end():]
        if (re.search(r"переда[еёю]|отправля[ею]", prefix, re.I) and _ROUTE_TAIL.match(tail)
                and not _EXTERNAL.search(tail) and not re.search(r"[;.!?]\s+\w|,\s*(?:а|но|если)\b", tail)):
            return " ".join(prefix.casefold().split())
    return ""


def _route_error(question, basis, quotes):
    if not (_ORIGIN.search(question) and _ID.search(question) and "выбран" in question.casefold()):
        return ""
    outcomes = basis.get("outcomes", [])
    if len(outcomes) != 2:
        return ""
    first = _sent_id(outcomes[0])
    if first and first == _sent_id(outcomes[1]):
        # A mandated data source can be observable even with equal payloads.
        if any(_ID.search(q) and _MANDATED_ORIGIN.search(q) for q in quotes):
            return ""
        return ("В обеих ветвях отправляется один идентификатор выбранного объекта. Если меняется "
                "только внутренний маршрут его получения, сними эту карточку. Для самостоятельного "
                "вопроса покажи различие в публичном контракте, значении, доступе или обязательном "
                "внешнем вызове и опору именно для этого различия.")
    return ""


def question_focus_error(finding, source_quotes):
    if not finding or not finding.get("question"):
        return ""
    basis = finding.get("question_basis", {})
    ids = set(finding.get("ids", ())) | set(basis.get("checked_ids", ()))
    quotes = [source_quotes[i] for i in ids if i in source_quotes]
    question = finding["question"]
    issues = [_initial_error(finding, basis, quotes), _route_error(question, basis, quotes)]
    # A pair of genuinely distinct wire/state decisions disguised as one
    # long question. The tests may still exercise all three lifecycle states.
    parts = [part.strip() for part in question.casefold().split("?") if part.strip()]
    asks_contract = any("запрос" in p and re.search(r"како[йю]|какие|каким", p) for p in parts)
    asks_initial = any(_INITIAL.search(p) and re.search(r"что |как |како|какие", p) for p in parts)
    if (len(parts) > 1 and asks_contract and asks_initial
            and re.search(r"чита|чтени|считыва", question, re.I)
            and re.search(r"после (?:замен|сохран|измен)", question, re.I)):
        issues.append("Вопрос объединяет контракт чтения, состояние до первой записи и повтор после "
                      "изменения. Оставь один предмет решения в вопросе. Чтение после замены проверь "
                      "в тесте. Сохрани отдельное решение о начальном значении у соответствующего кандидата. "
                      "Если карточке принадлежит весь контракт чтения, спроси о его ответе для исходного "
                      "и сохранённого состояний, а вызов и поля перечисли в тесте.")
    return " ".join(issue for issue in issues if issue)
