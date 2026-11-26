"""Compare explicit container capacities and accepted instances in the source."""

from collections import defaultdict
import re


_WORD = r"[^\W\d_]+"
_UPPER = re.compile(
    rf"\b(?P<subject>{_WORD})\s+(?:содержит|вмещает|включает|contains|holds)\s+"
    rf"(?:от\s+\d+\s+до|не более|максимум|до|at most|up to|between\s+\d+\s+and)\s+"
    rf"(?P<quantity>\d+\s+(?P<unit>{_WORD}))\b", re.I)
_INSTANCE = re.compile(
    rf"\b(?P<subject>{_WORD})\s+(?:из|с|of|with)\s+(?P<quantity>\d+\s+(?P<unit>{_WORD}))\b", re.I)
_ADMITTED = re.compile(r"\b(?:принима(?:ет|ют|ется|ются)|принят[аоы]?|разреша(?:ет|ют|ется|ются)|"
                       r"допуска(?:ет|ют|ется|ются)|допущен[аоы]?|accepted|accepts|permits|allows)\b", re.I)
_REFUSED = re.compile(r"\b(?:отклон\w*|запрещ\w*|нельзя|блокиру\w*|недопустим\w*|не\s+(?:принима|разреш|допуска|переда|отправ|"
                      r"сохраня|публику)\w*|reject\w*|forbid\w*|not\s+(?:allow|accept|permit|sent)\w*)\b", re.I)
_INTAKE = re.compile(r"\b(?:загру[зж]\w*|импорт\w*|upload\w*|import\w*)\b", re.I)
_ONWARD = re.compile(r"\b(?:публи[кч]\w*|экспорт\w*|переда\w*|передач\w*|отправ\w*|"
                     r"publish\w*|export\w*|send\w*|dispatch\w*)\b", re.I)
_EXCEPTION = re.compile(
    r"\b(?:отбира\w*|оставля\w*\s+только|усека\w*|обреза\w*|отбрасыва\w*|отфильтров\w*|фильтру\w*|"
    r"сокраща\w*|бер[её]т\s+(?:первые|последние)|преобразу\w*|удаля\w*|"
    r"исключени\w*\s+(?:для|составля)|предел\s+(?:применяется\s+только|не\s+применяется)|"
    r"truncat\w*|filter\w*|discard\w*|retain\w*\s+only|except\s+for)\b", re.I)
_NEGATION = re.compile(r"(?:\bне|\bбез|\bnot|\bnever)\s*$", re.I)
_ADJECTIVE = re.compile(r"(?:ого|его|ому|ему|ыми|ими|ую|юю|ая|яя|ое|ее|ий|ый|ой|ых|их)$", re.I)
_TARGET = re.compile(r"\b(?:до|первых|первые|последние|не более|first|last|to|at most)\s+(\d+)\b", re.I)
_GENERIC = {"каждый", "каждая", "каждую", "каждого", "любая", "любой", "любую", "такой", "такую"}
_TEXT_UNITS = (r"(?:Unicode\s+)?code[ -]points?|(?:UTF[- ]?(?:8|16|32)\s+)?code[ -]units?|"
               r"grapheme(?:\s+clusters?)?s?|bytes?|characters?|letters?")
_TEXT_QUANTITY = rf"(?P<quantity>(?P<number>\d+)\s+(?P<unit>{_TEXT_UNITS}))\b"
_TEXT_LIMIT = re.compile(
    rf"\breject\s+(?:(?:a|an|the|each|any)\s+)?(?P<subject>\w+)\s+(?:when|if)\s+"
    rf"(?:the\s+length\s+of\s+)?its\s+(?P<field>\w+)\s+(?:length\s+)?"
    rf"(?:exceeds|is\s+(?:longer\s+than|over)|contains\s+more\s+than)\s+{_TEXT_QUANTITY}", re.I)
_TEXT_INSTANCE = re.compile(
    rf"\b(?P<subject>\w+)\s+(?:(?:of|with)\s+|(?:with|whose)\s+(?P<field>\w+)\s+"
    rf"(?:of|containing|measuring|is|has)\s+){_TEXT_QUANTITY}", re.I)
_OTHER_PART = re.compile(r"\b(?:metadata|headers?|footers?|prefix(?:es)?|suffix(?:es)?|timestamps?|"
                         r"attributes?|fields?|annotations?|serialized|serialised|framing|overhead)\b", re.I)
_COMPOSITION = re.compile(r"\b(?:length|count\w*|measur\w*|includ\w*|compris\w*|consists?|"
                          r"combined|together|total|with)\b", re.I)
_LENGTH_TRANSFORM = re.compile(r"\b(?:truncat\w*|shorten\w*|trim\w*|clip\w*)\b", re.I)
_EXEMPT = re.compile(r"\b(?:is exempt from|does not apply to|is excluded from)\b", re.I)
_QUALIFIED = re.compile(r"\b(?:except|unless|only|provided\s+that|otherwise|however|if|but|and|"
                        r"when|for|including|combined|together)\b", re.I)
_CONDITIONAL_PREFIX = re.compile(r"\b(?:if|when|unless|except|only|provided|after|before|may|might|never|"
                                 r"not|without)\b", re.I)


def _unit_name(unit):
    return re.sub(r"[\s-]+", " ", unit.lower()).removesuffix("s")


def _text_exception(text, pair):
    subject, field = re.escape(pair["subject"]), re.escape(pair["length_field"])
    if not all(re.search(rf"\b{word}\b", text, re.I) for word in (subject, field)):
        return False
    if _EXEMPT.search(text) and re.search(r"\blimit\b", text, re.I):
        return any(m["subject"].lower() == pair["subject"] and int(m["number"]) == pair["accepted"]
                   and _unit_name(m["unit"]) == pair["unit"] and (m["field"] or pair["length_field"]).lower() == pair["length_field"]
                   for m in _TEXT_INSTANCE.finditer(text))
    for change in _LENGTH_TRANSFORM.finditer(text):
        prefix, suffix = text[:change.start()], text[change.end():]
        operand = (re.match(rf"\s+(?:(?:the|its)\s+)?(?:{subject}(?:'s)?\s+)?{field}\b", suffix, re.I)
                   or re.search(rf"\b{field}\s+(?:(?:must|shall)\s+be|is|gets)\s+$", prefix, re.I))
        if not operand or _NEGATION.search(prefix):
            continue
        target = re.search(rf"\b(?:to|at most|first)\s+{_TEXT_QUANTITY}", suffix, re.I)
        if target and _unit_name(target["unit"]) == pair["unit"] and int(target["number"]) <= pair["limit"]:
            return True
    return False


def _text_pairs(blocks, rows, claims):
    clauses = [(block.id, clause) for block in blocks for clause in _sentences(block.text)]
    examples = [(block, clause, m) for block, clause in clauses
                if _ADMITTED.search(clause) and not _REFUSED.search(clause)
                for m in _TEXT_INSTANCE.finditer(clause)]
    limits = [(block, m) for block, clause in clauses for m in _TEXT_LIMIT.finditer(clause)
              if not _QUALIFIED.search(clause[m.end():]) and not _CONDITIONAL_PREFIX.search(clause[:m.start()])]
    pairs = []
    for block, limit in limits:
        subject, field = limit["subject"].lower(), limit["field"].lower()
        unit, upper = _unit_name(limit["unit"]), int(limit["number"])
        entity = re.compile(rf"\b{re.escape(subject)}s?\b", re.I)
        compound = any(entity.search(clause) and _OTHER_PART.search(clause) and _COMPOSITION.search(clause)
                       for _, clause in clauses)
        competing_fields = any(m["subject"].lower() == subject and m["field"].lower() != field
                               and _unit_name(m["unit"]) == unit for _, m in limits)
        for example_block, clause, example in examples:
            if example["subject"].lower() != subject or _unit_name(example["unit"]) != unit:
                continue
            # «An item of N characters» can describe its text. It does not establish
            # a member's length when the record size includes other components.
            named = example["field"]
            if (named and named.lower() != field) or (not named and (field != "text" or compound or competing_fields)):
                continue
            observed = int(example["number"])
            tail = clause[example.end():]
            passive = re.match(r"\s+(?:long\s+)?(?:(?:is|was|must be|shall be|will be)\s+)?(?:accepted|permitted|allowed)\b", tail, re.I)
            active = re.search(r"\b(?:accepts|allows|permits)\s+(?:(?:a|an|the)\s+)?$", clause[:example.start()], re.I)
            if (observed <= upper or not (passive or active) or _QUALIFIED.search(tail)
                    or _CONDITIONAL_PREFIX.search(clause[:example.start()])):
                continue
            left, right = _claims_at(rows[block], limit["quantity"]), _claims_at(rows[example_block], example["quantity"])
            if not left or not right or set(left).intersection(right):
                continue
            pair = dict(subject=subject, length_field=field, unit=unit, limit=upper, accepted=observed,
                        intake_only=False, limit_ids=left, instance_ids=right)
            pair["qualification_ids"] = [row["id"] for row in claims if _qualifies(row["quote"], pair)]
            pairs.append(pair)
    return pairs


def _stem(word):
    # Only remove case endings. Keeping the lexical stem avoids conflating
    # different field names solely because their first few letters match.
    return re.sub(r"(?:ами|ями|ов|ам|ям|ах|ях|[аяыиуюье])$", "", word.casefold().replace("ё", "е"))


def _modifier(text, match):
    previous = re.search(rf"({_WORD})\s+$", text[:match.start("subject")])
    if not previous:
        return ""
    word = previous[1].lower()
    return _ADJECTIVE.sub("", word) if word not in _GENERIC and _ADJECTIVE.search(word) else ""


def _subject(text, match):
    return (_stem(match["subject"]), _modifier(text, match), _stem(match["unit"]))


def _sentences(text):
    return re.split(r"(?<=[.!?;])\s+|\n+", text)


def _claims_at(rows, phrase):
    return [r["id"] for r in rows if phrase in r["quote"]]


def _qualifies(text, pair):
    if "length_field" in pair:
        return any(_text_exception(clause, pair) for clause in _sentences(text))
    for clause in _sentences(text):
        terms = {_stem(word) for word in re.findall(_WORD, clause)}
        if not {pair["subject"], pair["unit"]} <= terms:
            continue
        if pair["intake_only"] and _ONWARD.search(clause) and _REFUSED.search(clause):
            return True
        if any(not _NEGATION.search(clause[:m.start()]) for m in _EXCEPTION.finditer(clause)) and not any(
                int(quantity) > pair["limit"] for quantity in _TARGET.findall(clause)):
            return True
    return False


def capacity_pairs(blocks, claims):
    rows = defaultdict(list)
    for row in claims:
        rows[row["block"]].append(row)
    limits, examples = [], []
    for block in blocks:
        for clause in _sentences(block.text):
            for match in _UPPER.finditer(clause):
                limits.append((block.id, clause, match))
            if _ADMITTED.search(clause) and not _REFUSED.search(block.text):
                examples.extend((block.id, clause, match) for match in _INSTANCE.finditer(clause))
    pairs = []
    for limit_block, limit_text, limit in limits:
        key = _subject(limit_text, limit)
        upper = int(limit["quantity"].split()[0])
        for example_block, example_text, example in examples:
            if key != _subject(example_text, example):
                continue
            observed = int(example["quantity"].split()[0])
            if observed <= upper:
                continue
            left = _claims_at(rows[limit_block], limit["quantity"])
            right = _claims_at(rows[example_block], example["quantity"])
            if not left or not right or set(left).intersection(right):
                continue
            pair = dict(subject=key[0], unit=key[2], limit=upper, accepted=observed,
                        intake_only=bool(_INTAKE.search(example_text) and not _ONWARD.search(example_text)),
                        limit_ids=left, instance_ids=right)
            pair["qualification_ids"] = [row["id"] for row in claims if _qualifies(row["quote"], pair)]
            pairs.append(pair)
    return pairs + _text_pairs(blocks, rows, claims)


def linked(pair, finding):
    ids = set(finding["ids"])
    return bool(ids.intersection(pair["limit_ids"]) and ids.intersection(pair["instance_ids"]))


def _conflict(pair, findings):
    return any(f["kind"] == "Дефект" and f["category"] == "Противоречивость" and linked(pair, f)
               for f in findings)


def unresolved_capacity(pair, findings, resolved):
    if _conflict(pair, findings):
        return False
    evidence = set(pair["qualification_ids"])
    for f in findings:
        if linked(pair, f) and evidence.intersection(f["ids"]):
            return False
    return not any(evidence.intersection(resolved.get(i, {}).get("supports", []))
                   for i in pair["limit_ids"] + pair["instance_ids"])


def missing_capacity_basis(pair, findings, decisions, originals):
    if _conflict(pair, findings):
        return []
    affected = [(i, decision) for i, decision in enumerate(decisions)
                if decision["id"] in originals and linked(pair, originals[decision["id"]])]
    for _, decision in affected:
        anchors = decision["case_check"]["anchors"]
        if any(a["id"] in pair["qualification_ids"] and _qualifies(a["quote"], pair) for a in anchors):
            return []
    return [i for i, _ in affected]


def diagnosis(pair):
    scope = (f"Для {pair['subject']} сопоставляется длина {pair['length_field']} в {pair['unit']}. "
             "Для другой меры или отдельного размера записи с заголовком нужна цитата из источника. "
             if "length_field" in pair else "")
    return (scope + f"Сопоставь предел {pair['limit']} ({', '.join(pair['limit_ids'])}) "
            f"и принятие {pair['accepted']} ({', '.join(pair['instance_ids'])}). "
            "При совпадающем объекте без прямо заданного фильтра или исключения это дефект "
            "противоречивости с основаниями из обоих правил. Для снятия или понижения нужны "
            "дословные основания из источника, объясняющие совместимость именно этого случая.")
