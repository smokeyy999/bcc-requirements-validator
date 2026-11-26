"""Relate a universal rule for automatic commands to a scheduled instance."""

from collections import defaultdict
import re


_WORD = r"[а-яa-z][а-яa-z-]*"
_COMMAND = re.compile(r"\bкоманд(?:а|у|ы|ой|е)?\s+(?:на\s+)?")
_ALL = re.compile(r"\b(?:все|любые)\s+(?:(?:следующие|последующие|поступающие)\s+)?автоматические\s+$")
_BLOCK = re.compile(r"\b(?:игнорир\w*|блокир\w*|запрещ\w*|отклон\w*|не\s+(?:выполня|исполня)\w*)\b")
_MACHINE = re.compile(r"\b(?:от\s+(?:расписания|таймера|планировщика)|по\s+(?:расписанию|таймеру)|"
                      r"по\s+сигналу\s+таймера)\b")
_ACTOR = re.compile(r"\b(?P<actor>планировщик|таймер)\s+(?:автоматически\s+)?(?:выполняет|исполняет)\s+$")
_MODE = re.compile(r"\b(?:при|в\s+(?:режиме|состоянии)|во\s+время)\s+")
_PERFORM = re.compile(r"\b(?:выполняется|исполняется|срабатывает|исполнена|выполнена)\b")
_MANUAL = re.compile(r"\b(?:после|только\s+при|требует)\s+(?:явного\s+|ручного\s+)?"
                     r"(?:подтверждения|разрешения|одобрения)\s+(?:оператор\w*|пользовател\w*|внешн\w+\s+систем\w*)\b|"
                     r"\b(?:после|требует)\s+(?:отдельного\s+)?(?:внешнего|ручного)\s+подтверждения\b|"
                     r"\b(?:является|считается)\s+(?:ручной|внешней)\b|\bвыполняется\s+вручную\b")
_EXCEPTION = re.compile(r"\b(?:кроме|за\s+исключением|исключени\w*\s+(?:для|составля\w+)|"
                        r"(?:правило|запрет)\s+не\s+распространяется)\b")
_VERB = re.compile(rf"\b({_WORD}(?:ет|ит|ют|ут|ат|ят))\b")


def _stem(word):
    return re.sub(r"(?:иями|ыми|ими|ого|его|ому|ему|ой|ей|ам|ям|ов|ев|ах|ях|[аияыеую])$", "", word)


def _terms(phrase):
    return tuple(_stem(w) for w in re.findall(_WORD, phrase))


def _mode_text(prefix):
    match = _MODE.search(prefix)
    if not match:
        return ""
    return re.split(r"[,.;]|\b(?:все|любые|команд\w*|правило|запрет)\b",
                    prefix[match.end():], maxsplit=1)[0].strip()


def _approved_manually(text):
    return any(not re.search(r"\bне\s+$", text[:m.start()]) for m in _MANUAL.finditer(text))


def _positive_action(action, tail):
    tail = re.split(r"[,;]|\b(?:а|но)\b", tail, maxsplit=1)[0]
    if _BLOCK.search(tail) or re.search(r"\b(?:не|возможно|может|после|если|только)\s+", tail):
        return False
    if _PERFORM.search(tail):
        return True
    # A source can name the effect with a cognate verb instead of «выполняется».
    # Remove a nominal suffix to obtain e.g. бронир-, публик-, откры-.
    root = re.sub(r"(?:ировани|аци|ени|ти|ни)$", "", action[0])
    return len(root) >= 4 and any(m[1].startswith(root) for m in _VERB.finditer(tail))


def _qualifies(text, mode, action, trigger):
    if not (_EXCEPTION.search(text) or _approved_manually(text)):
        return False
    for command in _COMMAND.finditer(text):
        rest = text[command.end():]
        source = _MACHINE.search(rest)
        if not source or (("таймер" in source[0]) != ("таймер" in trigger)):
            continue
        if _terms(_mode_text(text[:command.start()])) in ((), mode) and _terms(rest[:source.start()]) == action:
            return True
    return False


def scheduled_command_pairs(claims):
    rows = defaultdict(list)
    for row in claims:
        for text in re.split(r"[.!?;\n]", row["quote"].casefold().replace("ё", "е")):
            rows[text.strip()].append(row["id"])
    prohibitions, instances = [], []
    for text, ids in rows.items():
        for cmd in _COMMAND.finditer(text):
            prefix, rest = text[:cmd.start()], text[cmd.end():]
            universal = _ALL.search(prefix)
            if universal and (blocked := _BLOCK.search(rest)):
                action = rest[:blocked.start()].strip()
                mode = _mode_text(prefix[:universal.start()])
                conditional = re.search(r"\b(?:только|если|при|в случае)\b", rest[blocked.end():])
                if mode and action and not conditional:
                    prohibitions.append((mode, action, ids))
            if trigger := _MACHINE.search(rest):
                action = _terms(rest[:trigger.start()])
                mode = _terms(_mode_text(prefix))
                if (mode and action and not _approved_manually(text)
                        and _positive_action(action, rest[trigger.end():])):
                    instances.append((mode, action, trigger[0], ids))
            elif actor := _ACTOR.search(prefix):
                mode = _terms(_mode_text(prefix[:actor.start()]))
                if mode and not _approved_manually(text) and not re.search(r"[,;]|\b(?:если|при|после)\b", rest):
                    instances.append((mode, _terms(rest), actor["actor"], ids))
    pairs = []
    for mode_text, action_text, bans in prohibitions:
        mode, action = _terms(mode_text), _terms(action_text)
        for event_mode, event_action, trigger, scheduled in instances:
            if mode != event_mode or action != event_action or set(bans).intersection(scheduled):
                continue
            # A written exception or an explicit human approval can change the
            # scope. Bind that qualification to this operation and trigger.
            if not any(_qualifies(text, mode, action, trigger) for text in rows):
                pairs.append(dict(condition=mode_text, operation=action_text,
                                  trigger=trigger, prohibition_ids=bans, instance_ids=scheduled))
    return pairs


def linked(pair, finding):
    ids = set(finding["ids"])
    return bool(ids.intersection(pair["prohibition_ids"]) and ids.intersection(pair["instance_ids"]))


def missing_conflict(pair, findings):
    return not any(f["kind"] == "Дефект" and f["category"] == "Противоречивость" and linked(pair, f)
                   for f in findings)


def diagnosis(pair):
    return (f"Все автоматические команды одной операции в общем режиме запрещены "
            f"({', '.join(pair['prohibition_ids'])}), а для команды {pair['trigger']} в том же режиме "
            f"предписано исполнение ({', '.join(pair['instance_ids'])}). Сохрани дефект противоречивости "
            "с обеими цитатами. Гипотетическое исключение для машинного источника не изменяет квантор «все».")


INSTRUCTION = ("В scheduled_command_rules указаны общий запрет и частное исполнение одной операции. "
               "Команда по расписанию или таймеру входит в класс автоматических команд в указанном режиме. "
               "Проверь объект и исход при одном входе. Для каждого такого несовпадения опиши прямое "
               "противоречие с цитатами обеих сторон, без вымышленного ручного подтверждения.")
