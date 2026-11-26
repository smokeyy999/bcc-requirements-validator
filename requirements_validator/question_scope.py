"""Check the input domain and observation boundary of a proposed acceptance test."""

import re


def _pattern(expression):
    return re.compile(expression, re.I)


_IDENTIFIER = _pattern(r"идентификатор|identifier|serial number|серийн\w* номер|артикул|\b\w+_id\b|(?-i:\b\w+Id\b)")
_FIELD_NAME = re.compile(r"\b[A-Za-z]\w*Id\b|\b[A-Za-z]\w*_id\b", re.ASCII)
_WIDTH = _pattern(r"длин|размер|границ|предел|ограничени|единиц|length|size|limit|width")
_ALPHABET = _pattern(r"алфавит|кодировк|кириллиц|латиниц|многобайт|не.?ascii|unicode|utf.?\d+|"
                     r"байт|byte|code.?point|character set|alphabet|non.?ascii|multibyte")
_ADMITTED_TEXT = _pattern(r"(?:разреш|допус|принима|состо|содерж|включ|поддерж|ввод|любые|любой|"
                          r"allow|accept|contain|support|may|arbitrary|any).{0,75}"
                          r"(?:unicode|кириллиц|национальн\w* букв|многобайт|non.?ascii|multibyte|cyrillic|люб\w* символ)"
                          r"|(?:unicode|кириллиц|многобайт|non.?ascii|cyrillic).{0,50}(?:допуск|разреш|allowed|accepted)")
_EXAMPLE = _pattern(r"(?:например|пример|example|such as)\s*[:,]?\s*[`«\"']([\w.:-]+)"
                    r"|(?:\w+Id|\w+_id|identifier|идентификатор\w*)\s*[=:]\s*[`«\"']?([\w.:-]+)")
_RESTRICTED = _pattern(r"не\s+(?:допус|поддерж|принима|разреш)|запрещ|только ASCII|ASCII.only|"
                       r"not (?:permitted|supported|allowed)|only ASCII")
_RECIPIENT = r"(?:клиент\w*|пользовател\w*|получател\w*|адресат\w*|устройств\w*|recipient|client|user|device)"
_DELIVERY = r"(?:получ\w*|достав\w*|появ\w*|отображ\w*|receive\w*|deliver\w*|display\w*)"
_ENDPOINT = _pattern(_RECIPIENT + r".{0,70}" + _DELIVERY + "|" + _DELIVERY + r".{0,70}" + _RECIPIENT
                     + r"|фактическ\w* (?:доставк|получени)|end.to.end|сквозн\w* (?:срок|интервал)")
_TIMING = _pattern(r"срок|задержк|интервал|за какое время|по времени|предельн\w* врем|дедлайн|SLA|"
                   r"latency|deadline|time limit|how long|как быстро")
_STATE = _pattern(r"признак|флаг|статус\w* (?:отправ|переда)|отметк|отмеч\w*|помеч\w*|маркер|marker|flag|(?:delivery|dispatch|send) status|mark as")
_TRANSFER = _pattern(r"отправ|переда|переда[её]т|передач|направл|отсыла|постановк\w* в очеред|"
                     r"hand.?off|dispatch|enqueue|send|sent|forward|transfer")
_BOUND = _pattern(r"в течение|не позднее|до истечения|не более|не дольше|максимальн\w* задержк|"
                  r"within|no later than|at most|не превыша\w*")
_GOAL = _pattern(r"в момент|сразу|своевременно|оперативно|немедленно|promptly|immediately|in real time")
_RECEIPT = _pattern(r"квитанц\w* (?:о |от )?(?:получ|достав|клиент|устройств|адресат)|"
                    r"(?:получател|устройств|клиент|адресат)\w*.{0,35}(?:квитанц|подтвержда)|"
                    r"подтвержд\w* (?:доставк|получени)|acknowledg\w*|delivery receipt")
_INCLUSION = _pattern(r"(?:вход\w*|включ\w*|охватыва\w*|проверя\w*|требу\w*|нуж\w*|следует|достаточ\w*|ограничива\w*|"
                      r"предусмотр\w*|явля\w*|относи\w*|распространя\w*|долж\w*|оценива\w*)\s+ли\b|"
                      r"ли\b.{0,35}при[её]мк|заканчива\w* ли|только.{0,70}или|"
                      r"does acceptance|is .{0,45}(?:in scope|required)|should .{0,45}(?:include|measure)")
_RECEIVER_OBSERVATION = _pattern(r"(?:получ\w*|достав\w*|квитанц\w*).{0,28}" + _RECIPIENT + "|"
                                 + _RECIPIENT + r".{0,28}(?:получ\w*|подтвержд\w*)|"
                                 r"(?:delivery receipt|client acknowledgment|recipient confirmation)")
_CONDITIONAL = _pattern(r"\bесли\b|в случае|при (?:включ|положительн|подтвержд|согласовани)|только при|\bif\b|when included")
_BEFORE = _pattern(r"\bдо\b|перед|изначальн|исходн\w* состояни|\bbefore\b|\bprior to\b")
_AFTER = _pattern(r"после|по завершении|по факту|затем|при наступлении|\bafter\b|\bonce\b")
_NO_RECEIPT = _pattern(r"без (?:квитанц|подтвержд)|не (?:возвраща|переда|подтвержда|требу|предусмотр)|"
                       r"no (?:delivery )?(?:receipt|acknowledg)|not (?:returned|required|provided)")


def _supports_alphabet(quote):
    if _RESTRICTED.search(quote):
        return False
    if _ADMITTED_TEXT.search(quote):
        return True
    return any(any(ord(char) > 127 for char in (match[1] or match[2])) for match in _EXAMPLE.finditer(quote))


def _alphabet_evidence(finding, original, quotes):
    names = {name.replace("_", "").casefold() for name in _FIELD_NAME.findall(_wording(finding) + " " + _wording(original))}
    for quote in quotes:
        for clause in re.split(r"[;\n]|(?<=[.!?])\s+", quote):
            fields = {name.replace("_", "").casefold() for name in _FIELD_NAME.findall(clause)}
            if fields and names and not fields <= names:
                continue
            if not fields and not _IDENTIFIER.search(clause):
                continue
            if _supports_alphabet(clause):
                return True
    return False


def _wording(item):
    return " ".join(item.get(key, "") for key in ("topic", "question", "test", "scenario"))


def _kind(item):
    text = _wording(item)
    if _IDENTIFIER.search(text) and _WIDTH.search(text) and _ALPHABET.search(text):
        return "область значений идентификатора"
    if _TRANSFER.search(text) and _STATE.search(item.get("question", "") + " " + item.get("topic", "")):
        return "событие фиксации отправки"
    if _ENDPOINT.search(text) and _TIMING.search(text):
        return "граница измерения срока"
    return ""


def source_boundaries(blocks):
    """Give the model actual source blocks for a staged handoff, including any later observables."""
    deadlines = [block.id for block in blocks if _TRANSFER.search(block.text) and _BOUND.search(block.text)]
    if not deadlines:
        return {}
    goals = [block.id for block in blocks if _GOAL.search(block.text) and re.search(_RECIPIENT, block.text, re.I)]
    flags = [block.id for block in blocks if _STATE.search(block.text) and _TRANSFER.search(block.text)]
    if not goals and not flags:
        return {}
    return {"timed_handoff": deadlines, "recipient_goals": goals, "recorded_state": flags}


def identifier_limits(blocks):
    return any(_IDENTIFIER.search(block.text) and (
        _WIDTH.search(block.section + " " + block.text) or re.search(r"\d+\s*[-–…]\s*\d+", block.text)
    ) for block in blocks)


def candidate_scopes(candidates):
    return {item["id"]: kind for item in candidates if (kind := _kind(item))}


def unreviewed_boundaries(boundaries, claims, findings, resolved):
    """Every signalled handoff decision needs a matching finding or an explicit source-based closure."""
    missing = []
    for key, kind in (("recipient_goals", "граница измерения срока"), ("recorded_state", "событие фиксации отправки")):
        for block in boundaries.get(key, ()):
            ids = {c["id"] for c in claims if c["block"] == block
                   and (key == "recipient_goals" or _STATE.search(c["quote"]))}
            if not ids or ids.intersection(resolved):
                continue
            if not any(ids.intersection(f["ids"]) and _kind(f) == kind for f in findings):
                missing.append(f"{block}, {kind}: проверь это решение отдельно. Дай узкий вопрос с основанием "
                               "или запиши в resolved относящийся к решению ID, объяснение и опорные ID.")
    return missing


def scope_error(finding, original, source_quotes):
    if not finding or not finding.get("question"):
        return ""
    kind = _kind(finding) or _kind(original)
    if not kind:
        return ""
    proof = finding.get("question_basis", {})
    ids = set(finding["ids"]) | set(proof.get("checked_ids", []))
    quotes = [source_quotes[ident] for ident in ids if ident in source_quotes]
    question = finding["question"]
    if kind == "область значений идентификатора":
        if not _alphabet_evidence(finding, original, quotes):
            return ("Граничный тест идентификатора предполагает незаявленный алфавит. Сними самостоятельный "
                    "вопрос. Для сохранения укажи в checked_ids прямое разрешение такого значения или "
                    "пример действительного идентификатора с соответствующими символами.")
    elif kind == "событие фиксации отправки":
        observations = " ".join([question, finding["test"], proof.get("decision", ""), *proof.get("outcomes", [])])
        if (not any(_RECEIPT.search(q) and not _NO_RECEIPT.search(q) for q in quotes)
                and (_RECEIVER_OBSERVATION.search(observations)
                     or not (_BEFORE.search(finding["test"]) and _AFTER.search(finding["test"])))):
            return ("Сохрани вопрос о записываемом признаке и замени его и тест. Спрашивай, какое событие "
                    "на границе отправителя фиксирует отправку; проверяй состояние до и после этого события. "
                    "Получение на устройстве не является доступным отправителю подтверждением. "
                    "Для привязки к квитанции требуется её дословное основание в checked_ids.")
    elif (not _INCLUSION.search(question)
          or (_RECEIVER_OBSERVATION.search(finding["test"]) and not _CONDITIONAL.search(finding["test"]))):
        if (any(_TRANSFER.search(q) and _BOUND.search(q) for q in quotes)
                and not any(_ENDPOINT.search(q) and _BOUND.search(q) and
                            (not _TRANSFER.search(q) or _RECEIVER_OBSERVATION.search(q)) for q in quotes)):
            return ("Сохрани самостоятельный вопрос о границе приёмки и замени question и test. "
                    "Сначала уточни, включено ли получение у адресата в приёмку. "
                    "Лишь при положительном ответе уточняй границы измерения. "
                    "В обеих ветвях тест проверяет прямо установленный срок передачи.")
    return ""


SCOPE_INSTRUCTION = """
Проверь достижимость исходных данных и границы наблюдения у каждого вопроса.
Для идентификатора, назначаемого существующему объекту, тип string и диапазон длины сами по себе
не обещают выпуск идентификаторов с другим алфавитом, шириной символов или способом декодирования.
Предполагать, что такой объект существует, даже в условном вопросе, недостаточно. Оставляй проверку
байтов и символов, только если исходник разрешает такие значения или даёт фактический пример;
приведи соответствующее точное утверждение в проверенных основаниях. Если при всех заявленных
входах нет различия результатов, закрой сомнение с объяснением.
Если source_boundaries переданы, проверь каждую связь по указанным блокам и остальному документу.
В сквозной проверке свяжи каждую цель и каждый хранимый признак с самостоятельной карточкой
по соответствующему решению либо объясни ответ в resolved с относящимся к нему ID и опорными ID.
Сохрани два независимых решения, когда для них есть основания. Для качественной цели у адресата
при количественном сроке только на участке передачи спроси, входит ли получение у адресата
в приёмку вообще. Только если входит, уточняй начальное и конечное события. Тест в любом случае
проверяет заданный интервал отправителя, а измерение у адресата делает лишь при включении в приёмку.
Если хранимый признак отправки назван без момента его изменения, спроси, какое наблюдаемое
событие при передаче на стороне отправителя фиксирует этот признак. В тесте сравни состояние до
и после выбранного события. Стадия доставки получателю требует отдельного доступного отправителю
подтверждения. Если прямо описаны сквозной срок, квитанция или иной сигнал обратной связи,
сохрани этот договор и проверь его по источнику. Если автор уже определил и испытание, и событие,
заверши проверку без вопроса. Пара условий source_boundaries служит поводом для сверки, не вердиктом.
"""
