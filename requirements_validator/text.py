"""Compare review wording while preserving literal output, operators and signed values."""

import re


_TOKENS = re.compile(
    r'«([^»\n]*)»|“([^”\n]*)”|"([^"\n]*)"|`([^`\n]*)`|'
    r'\d+(?:[.,]\d+)?|\w+|[^\w\s.,!?;:«»"“”`]', re.UNICODE)


def text_key(text):
    tokens = []
    for match in _TOKENS.finditer(text):
        literal = next((value for value in match.groups() if value is not None), None)
        if literal is not None:
            # Exact case, punctuation and spaces may be the specified external value.
            tokens.append('"' + literal + '"')
        else:
            tokens.append(match.group().casefold().replace("−", "-"))
    return " ".join(tokens)


INTEGER_WORDS = {}
for sequence in (
        "ноль один два три четыре пять шесть семь восемь девять десять одиннадцать двенадцать тринадцать четырнадцать пятнадцать шестнадцать семнадцать восемнадцать девятнадцать",
        "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen"):
    INTEGER_WORDS.update({word: value for value, word in enumerate(sequence.split())})
for value, forms in enumerate(("нуля", "одна одно одну одного одной", "две двух двум двумя",
                               "трёх трех трём трем тремя", "четырёх четырех четырём четырем четырьмя",
                               "пяти", "шести", "семи", "восьми", "девяти", "десяти")):
    INTEGER_WORDS.update(dict.fromkeys(forms.split(), value))


_COMPOUND = re.compile(
    r"двадцат\w*|тридцат\w*|сорок\w*|(?:пят|шест|сем|восем|восьм)\w*десят\w*|девяност\w*|"
    r"сто|ста|двести|триста|четыреста|\w+(?:сот|стах|стам|стами)|тысяч\w*|миллион\w*|"
    r"цел(?:ая|ых|ые)|десятых|сотых|тысячных|"
    r"twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|million|point|and")


def simple_source_numbers(text):
    """Recognize isolated spelled integers. A component of a larger number is insufficient evidence."""
    text = text.casefold()
    words = list(re.finditer(r"[^\W\d_]+", text))
    values = set()
    for index, word in enumerate(words):
        value = INTEGER_WORDS.get(word[0])
        if value is None:
            continue
        before = after = ""
        if index and re.fullmatch(r"[\s-]+", text[words[index-1].end():word.start()]):
            before = words[index-1][0]
        if index+1 < len(words) and re.fullmatch(r"[\s-]+", text[word.end():words[index+1].start()]):
            after = words[index+1][0]
        if any(part in INTEGER_WORDS or _COMPOUND.fullmatch(part) for part in (before, after)):
            continue
        values.add(str(-value if before in {"минус", "minus", "negative"} else value))
    return values
