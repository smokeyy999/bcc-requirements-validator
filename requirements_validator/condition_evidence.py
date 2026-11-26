"""Distinguish the rule for a question's input condition from the opposite branch."""

import re


_END = r"(?:ый|ий|ой|ая|яя|ое|ее|ые|ие|ого|его|ей|ых|их|ом|ем|ым|им|ую|юю|ыми|ими|ому|ему|а|ы|о)?"
_STATES = (
    ("valid", True, r"(?:корректн|валидн)" + _END + r"|valid"),
    ("valid", False, r"(?:некорректн|невалидн)" + _END + r"|invalid"),
    ("active", True, r"активн" + _END + r"|активен|active"),
    ("active", False, r"неактивн" + _END + r"|неактивен|inactive"),
    ("connected", True, r"подключ[её]нн?" + _END + r"|connected"),
    ("connected", False, r"(?:отключ[её]нн?|отсоедин[её]нн?)" + _END + r"|disconnected"),
)
_PATTERNS = [(dimension, polarity, re.compile(r"\b(?:" + expression + r")\b", re.I))
             for dimension, polarity, expression in _STATES]
_WORD = r"[\w-]+"
_CONDITION = re.compile(r"\b(?:при|для|если|когда|if|when|for|on|while)\s+(?:(?:[\w-]+)\s+){0,3}$", re.I)
_PREDICATE = re.compile(r"\b(?P<name>[\w-]+)\s+(?:(?:is|are|был[ао]?|оказал(?:ся|ась)|признан[оаы]?)\s+)?$", re.I)
_MORE_RULES = re.compile(r";|[.!?]\s+\S|\b(?:иначе|независимо|однако|всегда|во всех случаях|"
                         r"в любом случае|в остальных случаях|а при|otherwise|regardless|always)\b", re.I)
_NEGATION = re.compile(r"\b(?:не|not|never)\s+$", re.I)
_NON_SUBJECT = {"при", "если", "для", "когда", "if", "when", "for", "while", "is", "are", "the", "a", "an"}
_FIELD = re.compile(r"\b(?:пол[яе]|параметра|атрибута|field|property|parameter)\s+[`«\"]?([A-Za-z][\w.-]*)", re.I)


def _subject(word):
    word = word.casefold()
    # The generic value and observation terms can describe the same input. For
    # named concepts such as an account or connection require its own noun.
    if re.fullmatch(r"(?:показани|значени)\w*|данн(?:ые|ых|ыми|ым)|вход(?:а|е|ом|у|ы)?|"
                    r"inputs?|values?|readings?|data", word):
        return "input"
    return re.sub(r"(?:ами|ями|ов|ам|ям|ах|ях|[аяыиуюье])$", "", word)


def _mentions(text, conditional=False):
    result = set()
    for family, polarity, pattern in _PATTERNS:
        for token in pattern.finditer(text):
            before = text[:token.start()]
            if _NEGATION.search(before) or (conditional and not _CONDITION.search(before)):
                return None
            following = re.match(r"\s+(" + _WORD + ")", text[token.end():])
            previous = _PREDICATE.search(before)
            predicate = re.search(r"\b(?:is|are|был[ао]?|признан[оаы]?)\s+$", before, re.I)
            name = following[1] if following else ""
            if previous and (not following or predicate):
                name = previous["name"]
            if not name or name.casefold() in _NON_SUBJECT:
                return None
            result.add((family, polarity, _subject(name)))
    return result


def direct_condition_evidence(finding, source_quotes):
    """Move an inapplicable conditional claim to the evidence checked for the question."""
    proof = finding.get("question_basis")
    if (finding.get("category") != "Полнота" or finding.get("kind") not in {"Дефект", "Предполагаемый пробел"}
            or not proof or not finding.get("question") or len(finding["ids"]) < 2
            or finding.get("proposal_options") or finding.get("proposal_anchors") or finding.get("reference")):
        return finding
    wording = " ".join((finding["question"], proof.get("decision", "")))
    focus = _mentions(wording)
    if not focus or len(focus) != 1:
        return finding
    family, polarity, subject = next(iter(focus))
    opposite = (family, not polarity, subject)
    field_names = {name.lower() for name in _FIELD.findall(wording)}
    for field in ("scenario", "test"):
        mentions = _mentions(finding.get(field, ""))
        if mentions is None or any(f == family and p != polarity for f, p, _ in mentions):
            return finding
    context = []
    for ident in finding["ids"]:
        quote = source_quotes.get(ident, "")
        source_fields = {name.lower() for name in _FIELD.findall(quote)}
        if source_fields and source_fields != field_names:
            continue
        if not _MORE_RULES.search(quote) and _mentions(quote, conditional=True) == {opposite}:
            context.append(ident)
    # Keep the author's obligation, sole sources, and option-specific evidence.
    # They can only be changed by an adjudication with a new positive basis.
    directs = [i for i in finding["ids"] if i not in context]
    if not context or proof.get("obligation_id") not in directs:
        return finding
    return dict(finding, ids=directs,
                evidence=[e for e in finding["evidence"] if e["id"] not in context],
                question_basis=dict(proof, checked_ids=list(dict.fromkeys([*proof["checked_ids"], *context]))))
