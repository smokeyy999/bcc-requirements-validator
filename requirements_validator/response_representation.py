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
                      r"|(?:завершить|выполнить)\s+(?:[\w-]+\s+){0,2}успешно\b|"
                      r"(?:on|after)\s+success|successful\s+(?:response|result|operation)|HTTP\s+2(?:[0-9]{2}|xx))", re.I)
_FORMAL_FIELD = re.compile(r"\b(?:пол(?:е|я|ю|ем|ей|ях)|атрибут\w*|параметр\w*|field|attribute|parameter)"
                           r"\s+(?:[«\"\x60]([\w.-]+)[»\"\x60]|([A-Za-z_][A-Za-z0-9_.-]*))", re.I)
_NEXT_FIELD = re.compile(r"\s*(?:,\s*(?:(?:и|and)\s+)?|\s+(?:и|and)\s+)"
                         r"(?:[«\"\x60]([\w.-]+)[»\"\x60]|([A-Za-z_][A-Za-z0-9_.-]*))", re.I)
_FIELD_SUBJECT = re.compile(r"\b(?:пол[еяю]|полей|поля[хм]|параметр\w*|атрибут\w*|признак\w*|"
                            r"fields?|attributes?|parameters?)\b", re.I)
_APPLIES = re.compile(r"\b(?:обязател\w*|допустим\w*|присутств\w*|отсутств\w*|гарантир\w*|"
                      r"включ\w*|в\s+каких|при\s+каких|для\s+каких|долж\w*|нуж\w*|"
                      r"required|optional|absent|present|include\w*|which)\b", re.I)
_NO_INPUT = re.compile(r"\b(?:без|отсутстви[ея]|нет|without|missing)\s+([\w-]+)", re.I)
_BRANCH_NAMES = {"success": "успешный исход", "other": "отдельно описанные отказы"}
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
    fields = []
    for match in _FORMAL_FIELD.finditer(question):
        fields.append(match[1] or match[2])
        end = match.end()
        while adjacent := _NEXT_FIELD.match(question, end):
            fields.append(adjacent[1] or adjacent[2])
            end = adjacent.end()
    return [name for name in dict.fromkeys(fields) if re.search(r"(?<!\w)" + re.escape(name) + r"(?!\w)", source)]


def _separate_input(test, conditions, described):
    # Reading an earlier response is not a distinct input. A directly exercised
    # missing input can be named without using the word "error".
    terms = _terms(described)
    for clause in re.split(r"[.;!?\n,]+", test):
        if _targets_promised_case(clause, conditions):
            continue
        for action in _EXERCISE.finditer(clause):
            target = clause[action.end():].strip()
            if _OBSERVATION.match(target):
                continue
            if (_FAILURE.search(target) and _terms(target) or
                    any(_terms(m[1]) & terms for m in _NO_INPUT.finditer(target))):
                return True
    return False


def _only_promised_test(test, conditions, source):
    return (_targets_promised_case(test, conditions) and not _distinct_branch(test, conditions, source)
            and not _separate_input(test, conditions, source))


def _anchored_source(candidate, source_quotes, extra=()):
    evidence = [ev for ev in candidate.get("evidence", []) if ev["id"] in source_quotes]
    ids = list(dict.fromkeys([*candidate.get("ids", ()), *(ev["id"] for ev in evidence), *extra]))
    quotes = dict.fromkeys([*(source_quotes[i] for i in ids if i in source_quotes), *(ev["quote"] for ev in evidence)])
    return [i for i in ids if i in source_quotes], list(quotes)


def branch_anchors(candidates, claims):
    """Select source-backed, branch-specific field questions before adjudication."""
    source_quotes = {c["id"]: c["quote"] for c in claims}
    anchors = []
    for candidate in candidates:
        question = candidate.get("question", "")
        if not question:
            continue
        ids, quotes = _anchored_source(candidate, source_quotes)
        source = "\n".join(quotes)
        fields = _contract_fields(question, source)
        if not fields:
            continue
        conditions = _branches([q for q in quotes if _promises_previous(q)])
        branch = _distinct_branch(question, conditions, source)
        # Some candidates cite the contract of another failure but omit the
        # rule for the control case. Their own citations still identify the
        # separate field obligation; do not borrow an unrelated source rule.
        if (not branch and not conditions and (_OTHER_ERRORS.search(question) or _EXCEPT.search(question))
                and (_FAILURE.search(source) or _FAIL_CODE.search(source))):
            branch = "other"
        if branch:
            anchors.append(dict(id=candidate["id"], branch=_BRANCH_NAMES[branch], fields=fields,
                                question=question, test=candidate["test"], source_ids=ids))
    return anchors


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


def _branch_issue(branch, current, fields, original, finding, conditions, source):
    question, test = finding["question"], finding["test"]
    prior_test = original.get("test", "")
    names = {name: re.compile(r"(?<!\w)" + re.escape(name) + r"(?!\w)") for name in fields}
    # A reference such as «этот параметр» can identify the field through the
    # dependent test. An explicitly different field cannot stand in for it.
    refers = (bool(_FIELD_SUBJECT.search(question)) and not _contract_fields(question, source)
              and not any(pattern.search(question) for pattern in names.values()))
    absent = [name for name, pattern in names.items()
              if not pattern.search(question) and not (refers and pattern.search(test))]
    test_branch = _distinct_branch(test, conditions, source)
    exercised = test_branch == branch
    if branch == "other" and not test_branch:
        exercised = _separate_input(test, conditions, source + "\n" + prior_test)
    # A paraphrase can leave the individual inputs to the test. Preserve the
    # object of the question: an explicit different branch or a question about
    # encoding prior values is a change of decision even if the test is intact.
    same_branch = (current == branch or
                   not current and exercised and not _targets_promised_case(question, conditions)
                   and bool(_APPLIES.search(question)))
    errors = []
    if not same_branch:
        errors.append(f"В редакции не установлена исходная ветвь «{_BRANCH_NAMES[branch]}»")
    if absent:
        errors.append("Отсутствует исходное поле " + ", ".join(absent))
    control_only = (test != prior_test and not exercised and _only_promised_test(test, conditions, source))
    if control_only:
        errors.append("Тест воспроизводит только контрольный отказ с возвратом прежних данных")
    if not errors:
        return ""
    detail = ". ".join(errors)
    original_test = f" Исходный тест — «{prior_test}»." if prior_test and (control_only or not same_branch) else ""
    return (f"{detail}. Исходная ветвь — {_BRANCH_NAMES[branch]}, поля — {', '.join(fields)}. "
            f"Исходный вопрос — «{original['question']}».{original_test} Если пара соответствует источнику, "
            "сохрани её без перефразирования. При замене спроси о том же поле на тех же входах и "
            "проверь его в ответе на самостоятельный запрос этой ветви.")


def representation_error(finding, original, source_quotes):
    if not finding or not finding.get("question"):
        return ""
    question = finding["question"]
    proof = finding.get("question_basis", {})
    _, quotes = _anchored_source(original, source_quotes, [*finding["ids"], *proof.get("checked_ids", [])])
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
        return _branch_issue(original_branch, current_branch, fields, original, finding, conditions, source)
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
Если переданы response_branch_anchors, это первоначальные вопросы и тесты кандидатов с полями
и условиями из данного документа. Проверь их по source_ids. Когда исходная пара уже годится,
сохрани её. Если нужен уточняющий вопрос, режим замены допускает дословный текст применимой пары.
При перефразировании сравни начальный и новый тест: участник, вход, ветвь ответа и проверяемое
поле должны по-прежнему отвечать на то же открытое решение.
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
