import unittest
from types import SimpleNamespace

from requirements_validator.engine import _finding
from requirements_validator.text import simple_source_numbers, text_key


class LiteralComparisonTests(unittest.TestCase):
    def test_review_preserves_external_codes_and_rejects_an_unsupported_constant(self):
        clauses = ["После двух наблюдений вернуть «UP».", "После двух наблюдений вернуть «up»."]
        by_id, blocks, anchors = {}, {}, []
        for index, clause in enumerate(clauses, 1):
            block = f"M{index:04d}"
            ident = f"R-{block}-01"
            blocks[block] = SimpleNamespace(id=block, text=clause, section="Датчик", location=str(index))
            by_id[ident] = dict(id=ident, block=block, quote=clause)
            anchors.append(dict(id=ident, quote=clause))
        options = [dict(**anchor, reading=f"После 2 наблюдений вернуть «{code}».", effect=f"Ответ «{code}».")
                   for code, anchor in zip(("UP", "up"), anchors)]
        candidate = dict(topic="Код ответа", severity="Существенная", reason="Различается регистр.",
                         scenario="Два наблюдения.", consequence="Разные байты ответа.", kind="Дефект",
                         category="Противоречивость", reference="", question="Какой код вернуть?",
                         test="Сравнить код ответа.", fix="", blocking=True, evidence=anchors, interpretations=options)
        self.assertTrue(_finding(candidate, by_id, blocks, {})["counted"])
        options[0]["reading"] = "После 9 наблюдений вернуть «UP»."
        with self.assertRaisesRegex(ValueError, "9"):
            _finding(candidate, by_id, blocks, {})

    def test_output_literals_preserve_case_signs_and_empty_space(self):
        for left, right in [('Result «ERR»', 'Result «err»'), ('Lamp "+"', 'Lamp "−"'),
                            ("Return `a/b`", "Return `ab`"), ('Field ""', 'Field " "'),
                            ("Limit < 5", "Limit ≤ 5"), ("Rise 5%", "Rise 5‰"),
                            ("Coordinates −4.5", "Coordinates 4.5")]:
            with self.subTest(left=left, right=right):
                self.assertNotEqual(text_key(left), text_key(right))

    def test_narrative_punctuation_and_equivalent_delimiters_are_normalized(self):
        self.assertEqual(text_key('RETURN, «Ab».'), text_key('Return "Ab"!'))
        self.assertEqual(text_key("value −4.5"), text_key("VALUE -4.5"))

    def test_simple_spelled_source_values_do_not_license_parts_of_compounds(self):
        self.assertEqual(simple_source_numbers("не меньше трёх, lower bound minus two"), {"3", "-2"})
        for text in ("twenty-one", "one hundred and two", "двадцати пяти", "девяносто два",
                     "three point five", "одна целая две десятых"):
            with self.subTest(text=text):
                self.assertEqual(simple_source_numbers(text), set())
