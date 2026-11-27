"""Check clear cases of Russian modal agreement without guessing ambiguous roles."""

import re


_AGREEMENT = {
    "должно": ("приложение", "устройство", "оборудование", "табло", "подразделение", "хранилище"),
    "должна": ("система", "подсистема", "служба", "платформа", "программа", "станция", "панель"),
    "должен": ("сервис", "сервер", "терминал", "контроллер", "клиент", "оператор", "пользователь"),
    "должны": ("приложения", "устройства", "системы", "сервисы", "клиенты", "контроллеры", "пользователи"),
}
_EXPECTED = {subject: modal for modal, subjects in _AGREEMENT.items() for subject in subjects}
_SUBJECT = r"(?P<subject>" + "|".join(_EXPECTED) + r")\b"
_MODAL = r"(?P<modal>долж(?:ен|на|но|ны))\b"
_VERB = r"(?:вызывать|вызвать|использовать|применять|применить|выбирать|выбрать|отправлять|отправить|читать|прочитать|сохранять|сохранить)"
_RESOURCE = (r"(?P<resource>(?:[a-zа-яё]+-)?(?:метод|формат|протокол|контракт|канал|маршрут|ресурс|"
             r"запрос|пакет|источник|параметр|команду|операцию|настройку|структуру|сообщение))\b")
_FRONTED_OBJECT = re.compile(r"\b(?:какой|какую|какое)\s+" + _RESOURCE + r"\s+" + _MODAL +
                             r"\s+" + _VERB + r"\s+" + _SUBJECT, re.I)
_DIRECT_SUBJECT = re.compile(r"(?:^|[?.!;]\s*|\b(?:как|когда|зачем|почему|где)\s+)" +
                             _SUBJECT + r"\s+" + _MODAL + r"(?:\s+ли)?\s+" + _VERB + r"\b", re.I)
_ACTS = (r"(?:(?:долж(?:ен|на|но|ны)|мож(?:ет|гут))\s+)?(?:чит[а-яё]*|счит[а-яё]*|выз[а-яё]*|"
         r"вызыв[а-яё]*|запрашива[а-яё]*|отправ[а-яё]*|сохран[а-яё]*|получ[а-яё]*|"
         r"использ[а-яё]*|примен[а-яё]*|выбира[а-яё]*|выбр[а-яё]*)(?<!ся)(?<!сь)\b")
_QUOTED = re.compile(r"`[^`\n]*`|«[^»\n]*»|\"[^\"\n]*\"")


def _is_actor(match, quotes):
    # Fronted inanimate objects can look identical to nominative subjects.
    # Require explicit source evidence for who performs the operation, and
    # preserve a genuine reverse call even when both parties are active.
    subject = re.escape(match["subject"])
    resource = re.escape(match["resource"].rsplit("-", 1)[-1])
    active = re.compile(r"\b" + subject + r"\s+" + _ACTS, re.I)
    reverse = re.compile(r"\b" + resource + r"(?:\s+[\w-]+){0,3}\s+" + _ACTS +
                         r"[^.;!?\n]{0,40}\b" + subject + r"\b", re.I)
    passive = re.compile(r"\b" + subject + r"\s+(?:вызыва|использу|запрашива)\w*(?:ся|сь)\b"
                         r"[^.;!?\n]{0,40}\b" + resource + r"(?:ом|ем|ами)\b", re.I)
    return any(active.search(q) for q in quotes) and not any(reverse.search(q) or passive.search(q) for q in quotes)


def question_language_error(finding, source_quotes):
    """Ask for a model repair only when the published question changes the actor."""
    if not finding or not finding.get("question"):
        return ""
    text = _QUOTED.sub("…", finding["question"]).casefold()
    ids = set(finding.get("ids", ())) | set(finding.get("question_basis", {}).get("checked_ids", ()))
    quotes = [source_quotes[i].casefold() for i in ids if i in source_quotes]
    for pattern in (_DIRECT_SUBJECT, _FRONTED_OBJECT):
        for match in pattern.finditer(text):
            expected = _EXPECTED[match["subject"]]
            if match["modal"] == expected:
                continue
            if pattern is _FRONTED_OBJECT and not _is_actor(match, quotes):
                continue
            return (f"Согласуй сказуемое с исполнителем «{match['subject']}» (форма «{expected}»). "
                    "В вопросе поставь исполнителя перед глаголом, сохрани предмет выбора и направление "
                    "действия из ТЗ. Перефразируй только язык вопроса. В зависимом тесте сохрани сценарий "
                    "и ожидаемый результат.")
    return ""


QUESTION_LANGUAGE_INSTRUCTION = """
Перед отправкой прочитай каждый вопрос автору как самостоятельное предложение. Проверь, кто
совершает действие по ТЗ, к чему оно относится, а также падеж, род и число. В вопросе с
вынесенным вперёд объектом согласуй «должен / должна / должно / должны» с исполнителем.
Если возможны два чтения, назови исполнителя перед сказуемым и используй прямой порядок слов.
При языковой правке сохрани открытое решение, участников, условие и ожидаемый результат теста.
"""
