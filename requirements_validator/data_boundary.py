"""Keep a stored quantity's unit separate from its interface representation."""

import re


_FIELD = (r"сумм\w*|порог\w*|длительност\w*|задержк\w*|ширин\w*|длин\w*|высот\w*|"
          r"масс\w*|вес\w*|расстоян\w*|объ[её]м\w*|температур\w*|стои(?:мост|мость)\w*|"
          r"amount|threshold|duration|latency|width|length|height|weight|mass|distance|volume|temperature|price")
_UNIT = (r"(?:милли|микро|кило|санти|нано)?(?:секунд|грамм|метр|литр|байт)\w*|"
         r"(?:milli|micro|kilo|centi|nano)?(?:second|gram|met(?:er|re)|lit(?:er|re)|byte)s?|"
         r"тиын\w*|тенге|рубл\w*|копе[йе]\w*|цент\w*|доллар\w*|евро|балл\w*|градус\w*|"
         r"cents?|dollars?|degrees?|points?|EUR|USD|KZT|kB|MB|GB|ms|kg|mm|cm|мс|кг|мм|см")
_PAIR = re.compile(r"\b(?P<field>" + _FIELD + r")\b(?:\s+[\w-]+){0,5}?\s+(?:в|in)\s+"
                   r"(?P<unit>" + _UNIT + r")\b", re.I)
_INPUT = re.compile(r"\b(?:вход\w*|получ(?:ить|ает|ают|ен\w*|аем\w*|ающ\w*)|поступ\w*|"
                    r"пода(?:ть|ёт|вать)|переда\w*|в (?:событи|сообщени|пакет)\w*|"
                    r"(?:событи|сообщени|пакет)\w*\s+(?:содерж|нес[её]т|включа)\w*|"
                    r"input|payload|receive\w*|sent|send\w*|transmit\w*|incoming|message contains)\b", re.I)
_STORE = re.compile(r"\b(?:хран\w*|сохран\w*|запис(?:ать|ыва\w*|ан\w*|ь|и|ь?ю)|"
                    r"(?:в|для)\s+(?:архив\w*|баз[уе]|таблиц\w*|хранилищ\w*)|"
                    r"stor(?:e|ed|es|age|ing)\b|persist\w*|in the database|in the archive)\b", re.I)
_CLAUSE = re.compile(r"[.;!?\n]|,\s*(?:затем|после чего|then)\b", re.I)
_OPEN = re.compile(r"\b(?:в как\w* единиц\w*|каков\w* единиц\w*|which units?|what units?)\b|"
                   r"\b(?:или|либо|or)\s+(?:в\s+|in\s+)?(?:" + _UNIT + r")\b", re.I)
_NEGATED = re.compile(r"\b(?:не|никогда не|not|never)\s*$", re.I)
_QUALIFIER = re.compile(r"\s+([\w-]+)\s+")


def _stem(word):
    return re.sub(r"(?:ами|ями|ах|ях|ов|ев|[ауыеияюь]|(?<=[a-z])s)$", "", word.casefold())


def _phase(clause, pair):
    """Use the nearest explicit operation governing the quantity, on either side of its name."""
    before_unit = clause[:pair.start("unit")]
    phases = [(m.start(), kind, m) for kind, pattern in (("input", _INPUT), ("store", _STORE))
              for m in pattern.finditer(before_unit)]
    if phases:
        _, kind, match = max(phases, key=lambda entry: entry[0])
        return "" if _NEGATED.search(before_unit[:match.start()]) else kind
    after = clause[pair.end():].split(",", 1)[0]
    for token in re.finditer(_INPUT.pattern + "|" + _STORE.pattern, after, re.I):
        if not _NEGATED.search(after[:token.start()]):
            return "store" if _STORE.fullmatch(token[0]) else "input"
    return ""


def _bindings(text):
    for clause in _CLAUSE.split(text):
        for match in _PAIR.finditer(clause):
            between = clause[match.end("field"):match.start("unit")]
            modifier = _QUALIFIER.match(between)
            name = modifier[1] if modifier else ""
            if name.casefold() in {"в", "in", "is", "must", "должна", "должен"} or _STORE.search(name) or _INPUT.search(name):
                name = ""
            yield (_stem(match["field"]), _stem(name), _stem(match["unit"])), _phase(clause, match), bool(_OPEN.search(clause))


def _same_quantity(left, right):
    field, modifier, unit = left
    return field == right[0] and unit == right[2] and (not modifier or not right[1] or modifier == right[1])


def storage_units(blocks, claims):
    """Find a unit at rest, its claim IDs, and independent input declarations for the same quantity."""
    declarations = [(block.id, quantity, phase) for block in blocks
                    for quantity, phase, uncertain in _bindings(block.text) if phase and not uncertain]
    inputs = [quantity for _, quantity, phase in declarations if phase == "input"]
    result = []
    for block, quantity, phase in declarations:
        if phase != "store" or any(_same_quantity(quantity, item) for item in inputs):
            continue
        ids = [c["id"] for c in claims if c["block"] == block and
               (any(_same_quantity(quantity, q) for q, *_ in _bindings(c["quote"])) or _STORE.search(c["quote"]))]
        if ids:
            result.append(dict(block=block, quantity=quantity, claim_ids=ids))
    return result


def data_boundary_error(finding, stored_units):
    if not finding or not finding.get("question") or not stored_units:
        return ""
    proof = finding.get("question_basis", {})
    ids = set(finding["ids"]) | set(proof.get("checked_ids", []))
    at_rest = [item["quantity"] for item in stored_units if ids.intersection(item["claim_ids"])]
    def assumed(text):
        return {tuple(known) for value, phase, uncertain in _bindings(text) if phase == "input" and not uncertain
                for known in at_rest if _same_quantity(value, known)}

    statements = (finding["question"], finding["test"], proof.get("decision", ""))
    branches = [assumed(text) for text in proof.get("outcomes", [])]
    # A genuine question about the wire unit may illustrate different encodings.
    # If both branches impose the stored unit, the purported choice does not release it.
    branches_impose = (set.intersection(*branches) if branches and _OPEN.search(finding["question"]) else any(branches))
    if any(assumed(text) for text in statements) or branches_impose:
        return ("Единица в приведённом источнике относится к записи или хранению величины. "
                "Замени вопрос и тест: сохрани выбор источника исходного значения и его входного "
                "представления. При наличии преобразования проверь его отдельно, затем сверь запись "
                "в заданной единице хранения. Обе ветви должны допускать согласованный формат входа. "
                "Единицу непосредственно на входе можно закрепить только по явному контракту входа.")
    return ""


BOUNDARY_INSTRUCTION = """
В stored_units найдены величины с единицей записи или хранения. Для каждой отдельно сверь источник
входного значения, формат события или запроса, преобразование и сохраняемое значение. Названная
единица записи сама по себе не задаёт формат на входе. В вопросе об источниках перечисляй открытые
входные значения без присвоения им единиц из схемы хранения. Если нужно, уточни их представление.
Тест прослеживает исходные значения, проверяет преобразование при необходимости и конечную запись
в требуемой единице. Две ветви о разных источниках значения не должны обе молчаливо требовать один
неустановленный формат входа. Прямо заданные единицы конкретного сообщения и схемы хранения сохрани.
"""
