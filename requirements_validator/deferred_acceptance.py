"""Distinguish a promised acceptance procedure from examples inferred from normal operation."""
from collections import defaultdict
import re


INSTRUCTION = """
В deferred_procedures перечислены прямо обещанные испытания конкретных действий. Для каждого
сопоставь указанное действие и исходное состояние с процедурой или примером во всём ТЗ.
Обычное правило реализации может подсказывать тестировщику опыт, но не определяет, какой опыт
обязан принять заказчик. Если процедура явно отложена, зафиксируй дефект полноты её содержания.
Спроси только про недостающую часть из missing_parts, сохрани известные шаги и результаты.
Варианты самой проверки обозначь как предложения автору, а не как действующее требование.
"""

_ACCEPT = r"(?:при[её]мочн\w*\s+(?:испытани\w*|проверк\w*|тест\w*|сценари\w*|процедур\w*)|(?:процедур\w*|поряд\w*|сценари\w*|критери\w*|методик\w*)\s+при[её]мк\w*|acceptance\s+(?:test|check|procedure|criteria|scenario)s?)"
_ACCEPTANCE = re.compile(r"\b" + _ACCEPT + r"\b", re.I)
_DEFER = re.compile(r"\b(?:(?:буд\w+|предстоит|планируется|предполагается)\s+(?:определ\w*|опис\w*|соглас\w*|подготов\w*|разработ\w*|уточн\w*)|"
                    r"(?:определ\w*|опис\w*|соглас\w*|уточн\w*)\s+(?:позже|позднее)|"
                    r"(?:пока\s+)?не\s+(?:определ[её]н\w*|описа[нт]\w*|задан\w*)|"
                    r"(?:will|to)\s+be\s+(?:defined|specified|agreed)|tbd)\b", re.I)
_ADMIN = re.compile(r"\b(?:срок\w*|дат[ауы]|расписани\w*|стоимост\w*|график\w*|длительност\w*|"
                    r"schedule|budget|date|duration)\b", re.I)
_OPTIONAL = re.compile(r"\b(?:при\s+необходимости|по\s+желанию|необязательн\w*|optional|if\s+needed)\b", re.I)
_CASE = re.compile(r"\b(?:при[её]мк\w*|при[её]мочн\w*|сценари\w*|пример\w*|испытани\w*|тест[а-я]*|"
                   r"acceptance|scenario|example|test(?:s|ing)?)\b", re.I)
_CASE_START = re.compile(r"(?<![^\n.!?])\s*(?:пример|сценарий|example|scenario)\b", re.I)
_SUBJECT = re.compile(r"\b(?:проверк\w*|испытани\w*|при[её]мк\w*|тест[а-я]*|"
                      r"test|check|procedure)\s+(?:(?:для|for|of|the)\s+)*"
                      r"(?:(?:кнопк\w*|команд\w*|операци\w*|функци\w*|действи\w*|button|command|operation)\s+)?"
                      r"(?P<name>«[^»]+»|\"[^\"]+\"|\x60[^\x60]+\x60|[\w-]+(?:\s+[\w-]+){0,3})", re.I)
_QUALIFIER = re.compile(r"\b(?:в\s+(?:режиме|состоянии|статусе)|in\s+(?:state|mode))\s+"
                        r"(?:«([^»]+)»|\"([^\"]+)\"|\x60([^\x60]+)\x60|([\w-]+))", re.I)
_LEAD = re.compile(r"^\s*(?:(?:[-*]|\d+[.)])\s*)?(?:шаг\w*|действи[ея]|услови[ея]|ожида\w*|результат|"
                   r"затем|далее|когда|тогда|допустим|given|when|then|step|expected|result)\b", re.I)
_STEP = re.compile(r"\b(?:шаг(?:и|\s+\d+)?|действи[ея]|step(?:\s+\d+)?|when|когда)\s*[:.—-]?\s+\S|"
                   r"\b(?:нажа[тл]\w*|нажм\w*|выбра[тл]\w*|выбер\w*|вызва[тл]\w*|вызов\w*|подат\w*|"
                   r"отправ\w*|запуст\w*|выполн\w*|включ\w*|ввест\w*|введ\w*|после\s+\w+|"
                   r"press|select|call|send|invoke|click|run|submit)\b", re.I)
_NAMED_STEP = re.compile(r"\b(?:наж\w*|выбер\w*|выбр\w*|вызов\w*|вызв\w*|запуст\w*|выполн\w*|"
                         r"press|select|invoke|click|run)\s+(?:(?:кнопк\w*|команд\w*|операци\w*|the)\s+)?"
                         r"[«\"\x60]([^»\"\x60]+)[»\"\x60]", re.I)
_OUTCOME = re.compile(r"\b(?:ожидаем\w*\s+(?:результат|исход|ответ)|результат(?:\s+при[её]мки)?|"
                      r"ожидается|критерий\s+успеха|тогда|then|expected(?:\s+(?:result|outcome))?|result)"
                      r"\s*[:=—,-]?\s+[\w«\"\x60]|"
                      r"\b(?:появля\w*|отобража\w*|переходи\w*|переш[её]л\w*|получа\w*|возвраща\w*|"
                      r"исполня\w*|станов\w*|зажига\w*|загор\w*|меняется|оста[её]тся|"
                      r"returns?|shows?|appears?|changes?|becomes?)\b", re.I)
_UNSPECIFIED = re.compile(r"\b(?:не\s+(?:указан|задан|известен|определ[её]н)\w*|штатн\w*|"
                          r"корректн\w*|успешн\w*|as expected|normally|unspecified)\b", re.I)
_TEST_TOPIC = re.compile(r"\b(?:при[её]мк\w*|при[её]мочн\w*|испытани\w*|(?:обязательн\w*|контрольн\w*)\s+проверк\w*|"
                         r"(?:шаг\w*|критери\w*|результат\w*|поряд\w*)\s+проверк\w*|"
                         r"test(?:s|ing)?|acceptance|pass\s+criterion)\b", re.I)


def _subject(sentence):
    # Exclude the promise itself, which would otherwise be parsed as the object.
    match = _DEFER.search(sentence)
    prefix = sentence[:match.start()] if match else sentence
    for found in _SUBJECT.finditer(prefix):
        name = found["name"]
        if name.startswith(("«", '"', chr(96))):
            return name[1:-1].strip()
        name = re.split(r"\s+(?:в|при|для|на|долж\w*|обязател\w*|буд\w*|is|in|must)\b", name,
                        maxsplit=1, flags=re.I)[0]
        if not re.match(r"(?:буд\w*|долж\w*|при[её]м\w*|обязател\w*|is|will|must)\b", name, re.I):
            return name.strip()
    return ""


def _case_parts(blocks, subject, state):
    """Only an explicitly framed example/procedure supplies a contractual test."""
    parts = []
    name = re.compile(r"(?<!\w)" + re.escape(subject) + r"(?!\w)", re.I)
    for i, block in enumerate(blocks):
        body = block.text
        heading = block.section.split(" / ")[-1]
        # Keep continued Gherkin/step lists together without joining scenarios.
        for next_block in blocks[i+1:]:
            if next_block.section != block.section or not _LEAD.search(next_block.text):
                break
            body += "\n" + next_block.text
        starts = [m.start() for m in _CASE_START.finditer(body)]
        slices = zip([0, *starts], [*starts, len(body)])
        for start, end in slices:
            concrete = [s for s in re.split(r"(?<=[.!?])\s+|[\n;]+", body[start:end])
                        if not _DEFER.search(s)]
            example = "\n".join(concrete)
            context = heading + "\n" + example
            condition = re.split(r"\b(?:ожидаем\w*\s+(?:результат|исход)|тогда|then|expected)\b",
                                 context, maxsplit=1, flags=re.I)[0]
            if not name.search(context) or state and state.casefold() not in condition.casefold():
                continue
            if not (_CASE.search(context) or
                    re.search(r"\b(?:когда|when)\b.+\b(?:тогда|then)\b", example, re.I | re.S)):
                continue
            actions = _NAMED_STEP.findall(example)
            if actions and not any(name.fullmatch(action) for action in actions):
                continue
            step = bool(_STEP.search(example))
            outcome = any(_OUTCOME.search(s) and not _UNSPECIFIED.search(s) for s in concrete)
            parts.append((step, outcome))
    return parts


def promised_procedures(blocks, claims):
    """Return source-linked gaps in an expressly deferred test for a named subject."""
    rows = defaultdict(list)
    for claim in claims:
        rows[claim["block"]].append(claim)
    result = []
    blocks = list(blocks)
    for i, block in enumerate(blocks):
        sentences = re.split(r"(?<=[.!?])\s+|[\n;]+", block.text)
        for j, sentence in enumerate(sentences):
            marker = _DEFER.search(sentence)
            acceptance = _ACCEPTANCE.search(sentence)
            if not marker or not acceptance or _ADMIN.search(sentence[:max(marker.start(), acceptance.start())]):
                continue
            previous = sentences[j-1] if j else ""
            previous_id = block.id
            if not previous and i and blocks[i-1].section == block.section:
                previous, previous_id = blocks[i-1].text, blocks[i-1].id
            local_subject = _subject(sentence)
            subject = local_subject or _subject(previous)
            if not subject:
                continue
            basis = sentence if local_subject else previous + " " + sentence
            if _OPTIONAL.search(basis):
                continue
            qualifier = _QUALIFIER.search(basis)
            state = next((g for g in qualifier.groups() if g), "") if qualifier else ""
            coverage = _case_parts(blocks, subject, state)
            if (True, True) in coverage:
                continue
            missing_parts = [part for n, part in enumerate(("шаг испытания", "наблюдаемый результат"))
                             if not any(pair[n] for pair in coverage)]
            if not missing_parts:
                missing_parts = ["какой результат ожидается именно на указанном шаге"]
            ids = [c["id"] for key in dict.fromkeys((block.id, previous_id)) for c in rows[key]
                   if marker[0].casefold() in c["quote"].casefold() or subject.casefold() in c["quote"].casefold()]
            if ids:
                result.append(dict(block=block.id, subject=subject, state=state, claims=ids,
                                   source=basis.strip(), missing_parts=missing_parts))
    return result


def linked(procedure, finding):
    return bool(set(procedure["claims"]).intersection(finding["ids"]))


def missing(procedure, findings):
    for finding in findings:
        if not (linked(procedure, finding) and finding.get("counted") and finding.get("category") == "Полнота"):
            continue
        wording = " ".join(finding.get(key, "") for key in ("topic", "reason", "consequence", "question"))
        if _TEST_TOPIC.search(wording):
            return False
    return True


def diagnosis(procedure):
    return (f'{procedure["block"]}: у прямо отложенного испытания «{procedure["subject"]}» '
            f'не определены {", ".join(procedure["missing_parts"])}. Нужна карточка полноты с дословным '
            'основанием. Предложение тестировщика по штатному поведению не заменяет обещанную процедуру.')
