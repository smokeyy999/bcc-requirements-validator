"""Keep the promised error payload fixed while reviewing its representation."""

import re


_OLD = r"(?:прежн\w*|предыдущ\w*|стар\w*|ранее сохран[её]нн\w*|previous|prior|old|original)"
_RETURN = r"(?:верн(?:уть|[её]т)|возвраща(?:ть|ется|ет|ются|ют)|переда(?:ть|[её]т)|returns?|returning|includes?)"
_FAILURE = re.compile(r"отклон|отказ|ошибк|неверн|недопустим|\b(?:reject\w*|fail\w*|error|invalid)\b", re.I)
_PROMISE = re.compile(r"\b" + _RETURN + r"\s+(?:(?:клиенту|вызывающему|the|to the client)\s+)?"
                      r"(?:в (?:теле )?ответ[ае] |in the response )?" + _OLD + r"\b", re.I)
_RESPONSE = re.compile(r"ответ|клиент|получател|вызывающ|результат|\b(?:response|payload|client|caller|error)\b", re.I)
_STORAGE_DESTINATION = re.compile(r"\s+(?:в (?:базу|хранилище|память)|to (?:the )?(?:store|database))\b", re.I)
_NONMANDATORY = re.compile(r"(?:не|можно|разрешено|допускается|может|may|optionally|must not|do not)\s+$", re.I)
_PRIOR = re.compile(_OLD + r"|до (?:запроса|операции|вызова|отказа)|исходн\w* значени|"
                    r"(?:свер\w*|сравн\w*|сопостав\w*)[^.;!?]{0,40}\bс исходными\b|"
                    r"заранее (?:сохран|задан)|предварительно (?:задан|сохран)", re.I)
_SHAPE = re.compile(r"\b(?:как(?:ой|ое|ом|ого|ие|им|ими|их|ов[аоы]?)?|где)\b|"
                    r"\b(?:how|where|which|what)\b", re.I)
_BODY = re.compile(r"пол[еяю]|полях|тело|теле|тела|структур|формат|представ|кодиров|вложен|атрибут|"
                   r"схем|ключ|вид[еау]|возвращ[аёе]нн|извлеч|прочита|field|body|schema|encod|format|attribute|structure", re.I)
_ASK_RETURN = re.compile(r"возвращ|верн|переда|выда|сообща|содерж|включ|получ|\b(?:return|contain|receive|include)", re.I)
_OPTIONAL = re.compile(r"(?:обязательн\w*|нуж\w*|мож\w*|долж\w*|обязан\w*|требу\w*|следует|достаточ\w*|допустим\w*)\s+ли\b|"
                       r"или (?:достаточно|только|можно)|^(?:must|should|may|does|is it enough)\b", re.I)
_STORAGE_ONLY = re.compile(r"(?<!не )\b(?:только|лишь|достаточно)\s+(?:(?:сохран\w*|ост\w*|восстанов\w*)\s+){0,3}"
                           r"(?:в (?:базе|хранилище|памяти)|сохранить)|"
                           r"без (?:передачи|возврата) (?:этих|прежн|предыдущ)|"
                           r"only (?:in (?:the )?(?:database|store)|preserv|stor)|persistence alone", re.I)
_OMIT_ACCEPTED = re.compile(r"(?:без " + _OLD + r".{0,45}(?<!не )\b(?:допускается|допустим|проходит)|"
                            r"(?:переда\w*|верн\w*|включ\w*).{0,30}(?:не требу\w*|необязател\w*))", re.I)
_PROHIBITION = re.compile(r"не (?:включать|передавать|возвращать)|запрещ\w* (?:передавать|возвращать)|"
                          r"must (?:not|never) (?:include|return|send)", re.I)
_NAMED_FIELD = re.compile(r"(?:в (?:отдельном )?поле|in (?:the )?field)\s+[`«\"]([\w.-]+)[`»\"]", re.I)
_FIELD_ONLY = re.compile(r"в каком (?:именно )?поле\b|\b(?:which|what) field\b", re.I)
_DETAIL = re.compile(r"структур|тип\b|тип[ае]\b|формат|кодиров|вложен|внутри|structure|format|type\b|encod", re.I)
_CHOICE = re.compile(r"\b(?:или|либо|or)\b", re.I)
_ENCODING = re.compile(r"вложен|отдельн\w* пол|плоск\w*|един\w* объект|одн\w* пол|nested|flat|separate fields|single field", re.I)
_CONDITION = re.compile(r"\b(?:при|если|когда|when|if|on|in case of)\s+([^,.;:\n]+)", re.I)
_OTHER_ERRORS = re.compile(r"\b(?:проч\w*|друг\w*|остальн\w*|ин(?:ых|ые|ом|ый|ой|ого)|"
                           r"other|remaining)\s+(?:описанн\w*\s+)?(?:ошиб\w*|отказ\w*|неуспешн\w*|"
                           r"отклон\w*|ошибочн\w*|errors?|failures?|rejections?)\b", re.I)
_EXCEPT = re.compile(r"\b(?:кроме|помимо|за исключением|except(?:\s+for)?|other than|excluding)\s+"
                     r"(?:(?:случа\w*|ошиб\w*|ветв\w*)\s+)?([^,?;.!]+)", re.I)
_SUCCESS = re.compile(r"\b(?:при\s+успехе|(?:при|после)\s+успешн\w*|успешн\w*\s+(?:ответ|ветв|исход|сохран)"
                      r"|(?:on|after)\s+success|successful\s+(?:response|result|operation)|HTTP\s+2(?:[0-9]{2}|xx))", re.I)
_FORMAL_FIELD = re.compile(r"\b(?:пол(?:е|я|ю|ем|ей|ях)|атрибут\w*|параметр\w*|field|attribute|parameter)"
                           r"\s+(?:[«\"\x60]([\w.-]+)[»\"\x60]|([A-Za-z_][A-Za-z0-9_.-]*))", re.I)
_FAIL_CODE = re.compile(r"(?<!\w)[45]\d\d(?!\w)")
_EXERCISE = re.compile(r"\b(?:проверить|вызвать|воспроизвести|смоделировать|отправить|подать|"
                       r"повторить|test|trigger|simulate|submit|exercise)\s+", re.I)
_OBSERVATION = re.compile(r"(?:(?:возвращ[её]нн\w*|полученн\w*|опубликованн\w*|прежн\w*|тот\s+же|"
                          r"the|returned|received|same)\s+)*(?:HTTP\b|код\w*|статус\w*|тел[оае]|поле|поля|"
                          r"чтени\w*|считывани\w*|извлечени\w*|наблюдени\w*|наличие|значени\w*|"
                          r"результат\w*|сообщени\w*|ответ\w*|что\b|code|status|body|reading|inspection|"
                          r"field|value|message|result|response)\b", re.I)
_SCOPE_WORDS = re.compile(r"[^\W\d_]+", re.UNICODE)
_GENERAL = re.compile(r"ошиб\w*|отказ\w*|отклон\w*|неуспеш\w*|неверн\w*|некоррект\w*|недопустим\w*|"
                      r"случа\w*|получени\w*|возникновени\w*|операци\w*|запрос\w*|значени\w*|"
                      r"люб\w*|кажд\w*|всех|всяк\w*|при|для|an?|any|all|every|the|of|in|for|is|was|"
                      r"invalid|error|failure|reject\w*|request|operation", re.I)


def _terms(text):
    return {re.sub(r"(?:ами|ями|ой|ей|ам|ям|ах|ях|ом|ем|[аяыиуюео])$", "", word)[:5]
            if re.fullmatch(r"[а-яё]+", word) else word
            for word in _SCOPE_WORDS.findall(text.casefold()) if len(word) > 2 and not _GENERAL.fullmatch(word)}


def _branches(promises):
    conditions = []
    for quote in promises:
        for sentence in re.split(r"[.;\n]+", quote):
            promise = _PROMISE.search(sentence)
            if not promise or not _promises_previous(sentence):
                continue
            condition = _CONDITION.search(sentence[:promise.start()])
            conditions.append(_terms(condition[1]) if condition else set())
    return conditions


def _targets_promised_case(text, conditions):
    # A valid input can be present alongside an invalid one. Only compare the
    # object of rejection, not all nouns somewhere in the test.
    for match in _FAILURE.finditer(text):
        after = re.match(r"\w*\s+((?:[\w-]+\s+)?[\w-]+)", text[match.end():])
        before = re.search(r"([\w-]+)\s+$", text[:match.start()])
        following = after[1].split() if after else []
        words = following[:2] if following and _GENERAL.fullmatch(following[0]) else following[:1]
        if before and not words:
            words.append(before[1])
        if any(_terms(" ".join(words)) & condition for condition in conditions):
            return True
    return False


def _distinct_branch(question, conditions, source):
    # A separate success branch is meaningful only if the source mentions success.
    success, failure = _SUCCESS.search(question), _FAILURE.search(question)
    explicit_case = _targets_promised_case(question, conditions)
    if (success and not explicit_case and (not failure or success.start() < failure.start())
            and re.search(r"успе[хш]|success|HTTP\s+2\d\d", source, re.I)):
        return "success"
    if not conditions or not all(conditions):
        return ""
    known = set.union(*conditions)
    alternative = "\n".join(line for line in source.splitlines() if not _promises_previous(line)
                            and (_FAILURE.search(line) or _FAIL_CODE.search(line)))
    if not alternative:
        return ""
    if any(_terms(m[1]) & known for m in _EXCEPT.finditer(question)):
        return "other"
    other = _OTHER_ERRORS.search(question)
    if other:
        context = re.match(r"\s+((?:[\w-]+\s+){0,2}[\w-]+)", question[other.end():])
        if not context or not _terms(context[1]).intersection(known):
            return "other"
    specific_codes = set(_FAIL_CODE.findall(question)) & set(_FAIL_CODE.findall(source))
    # A bare HTTP code can cover the explicitly promised rejection, too. Require
    # another described failure condition before treating the code as independent.
    for match in _CONDITION.finditer(question):
        clause = re.split(r"\b(?:долж\w*|обяза\w*|нуж\w*|следует|надо|верн\w*|возвращ\w*|содерж\w*|поле|"
                          r"переда\w*|выда\w*|включ\w*|does|should|must|return|contain|field)\b",
                          match[1], maxsplit=1, flags=re.I)[0]
        terms = _terms(clause)
        if _FAILURE.search(clause) and terms and not terms & known and terms & _terms(alternative):
            return "other"
    if len(specific_codes) > 1 and not explicit_case:
        return "other"
    return ""


def _contract_fields(question, source):
    fields = [match[1] or match[2] for match in _FORMAL_FIELD.finditer(question)]
    return [name for name in dict.fromkeys(fields) if re.search(r"(?<!\w)" + re.escape(name) + r"(?!\w)", source)]


def _only_promised_test(test, conditions, source):
    if not _targets_promised_case(test, conditions) or _distinct_branch(test, conditions, source):
        return False
    # A control for the known branch may follow an independent failing input.
    # Reading the same response again does not introduce a second experiment.
    for clause in re.split(r"[.;!?\n,]+", test):
        if not _FAILURE.search(clause) or _targets_promised_case(clause, conditions):
            continue
        for action in _EXERCISE.finditer(clause):
            target = clause[action.end():].strip()
            if _FAILURE.search(target) and _terms(target) and not _OBSERVATION.match(target):
                return False
    return True


def _promises_previous(quote):
    for sentence in re.split(r"[.;\n]+", quote):
        if not (_FAILURE.search(sentence) and _RESPONSE.search(sentence)):
            continue
        for match in _PROMISE.finditer(sentence):
            after = sentence[match.end():].split(",", 1)[0]
            if not _NONMANDATORY.search(sentence[:match.start()]) and not _STORAGE_DESTINATION.search(after):
                return True
    return False


def response_obligations(blocks):
    return [block.id for block in blocks if _promises_previous(block.text)]


def _names_previous_field(quote):
    for match in _PROMISE.finditer(quote):
        # A field bound to a second object (e.g. the error code) does not name
        # the field containing the first object.
        object_phrase = re.split(r"[,.;\n]|\b(?:и|and)\b", quote[match.end():], maxsplit=1, flags=re.I)[0]
        if _NAMED_FIELD.search(object_phrase):
            return True
    return False


def representation_error(finding, original, source_quotes):
    if not finding or not finding.get("question"):
        return ""
    question = finding["question"]
    proof = finding.get("question_basis", {})
    ids = set(finding["ids"]) | set(original["ids"]) | set(proof.get("checked_ids", []))
    quotes = [source_quotes[ident] for ident in ids if ident in source_quotes]
    promises = [quote for quote in quotes if _promises_previous(quote)]
    if not promises:
        return ""
    source = "\n".join(quotes)
    conditions = _branches(promises)
    original_question = original.get("question", "")
    original_branch = _distinct_branch(original_question, conditions, source)
    current_branch = _distinct_branch(question, conditions, source)
    fields = _contract_fields(original_question, source) if original_branch else []
    if fields:
        names = [re.compile(r"(?<!\w)" + re.escape(name) + r"(?!\w)") for name in fields]
        changed_test = finding["test"] != original.get("test")
        if (original_branch != current_branch or not all(name.search(question) for name in names)
                or changed_test and _only_promised_test(finding["test"], conditions, source)):
            return (f"Исходный вопрос о применимости поля {', '.join(fields)} относится к отдельно указанной "
                    "ветви ответа. Сохрани в вопросе и тесте именно это условие и поле. Другая ветвь с "
                    "обязательным возвратом прежнего состояния не определяет контракт этой ветви.")
    if current_branch or not (_PRIOR.search(question) and (_ASK_RETURN.search(question) or _BODY.search(question))):
        return ""
    # A rule explicitly excluding those values from the error payload is an
    # actual competing requirement. An example with an unknown input is not.
    if any(_FAILURE.search(q) and _RESPONSE.search(q) and
           any(_PRIOR.search(q[m.end():].split(".", 1)[0]) for m in _PROHIBITION.finditer(q)) for q in quotes):
        return ""
    if (_FIELD_ONLY.search(question) and not _DETAIL.search(question)
            and any(_names_previous_field(q) for q in promises)):
        return "В том же правиле прямо названо поле прежних данных при отказе. Сними уже отвеченный вопрос о названии поля."
    options = [v["effect"] for v in finding.get("proposal_options", [])]
    branches = [*proof.get("outcomes", []), *options]
    test = finding["test"]
    choices = _CHOICE.split(question)
    concrete_shapes = len(choices) == 2 and all(_ENCODING.search(part) for part in choices)
    if (((_SHAPE.search(question) and _BODY.search(question) and not _OPTIONAL.search(question)) or concrete_shapes)
            and _PRIOR.search(test) and _BODY.search(test)
            and not any(_STORAGE_ONLY.search(b) or _OMIT_ACCEPTED.search(b) for b in branches)):
        return ""
    return ("При отказе источник прямо требует вернуть прежние данные получателю. Оставь самостоятельный "
            "вопрос только о полях или структуре ответа, если представление ещё открыто. В тесте задай "
            "известное состояние, вызови отказ и сверь фактически возвращённые значения с исходными. "
            "Оба исхода должны сохранять возврат прежних значений и различаться их представлением. "
            "Для ошибочной неоднозначности выбери action=уточнить, верни опорные ID в supports и замени "
            "вопрос с тестом. При полностью определённом представлении сними решённый вопрос.")


REPRESENTATION_INSTRUCTION = """
Для returned_state_on_error сверяй отдельно исход операции и его представление для получателя.
Сопоставляй условие именно того отказа, для которого написано правило, с открытым решением
кандидата. Упоминание этой нормы в checked или в известной части теста не переносит её на успех
и остальные ошибки. Для вопроса об обязательности конкретного поля в других описанных ветвях
сохрани эти ветви и это поле в вопросе и тесте. Не подменяй их форматом возврата прежних данных.
Если правило требует вернуть прежние данные вместе с отказом, возврат значений уже обязателен.
Сопоставь с контрактом именно этой ветви. Поля для успеха, образец без запроса и сохранность в
хранилище сами по себе не определяют представление прежних данных при отказе. Когда в правиле
не указаны поля или структура ответа, оставь владельцу один уточняющий вопрос о таком представлении.
Зависимый тест задаёт известные прежние значения, воспроизводит отказ, считывает их из ответа
и сравнивает с исходными. Обе ветви различаются представлением одних и тех же возвращённых данных.
Если представление уже задано, укажи его в resolved. Если источник требует только сохранить
состояние внутри системы, не добавляй обязанность вернуть его. Если для того же отказа прямо
предписано исключить прежние значения из ответа, проверь обе нормы как реальный конфликт.
"""
