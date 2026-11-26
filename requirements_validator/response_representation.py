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
    if not (_PRIOR.search(question) and (_ASK_RETURN.search(question) or _BODY.search(question))):
        return ""
    proof = finding.get("question_basis", {})
    ids = set(finding["ids"]) | set(original["ids"]) | set(proof.get("checked_ids", []))
    quotes = [source_quotes[ident] for ident in ids if ident in source_quotes]
    promises = [quote for quote in quotes if _promises_previous(quote)]
    if not promises:
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
