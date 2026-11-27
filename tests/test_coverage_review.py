from copy import deepcopy
import json
from types import SimpleNamespace
import unittest

from requirements_validator import engine
from requirements_validator.coverage_review import _reconcile, supplement


def block(i, text):
    return SimpleNamespace(id=f"B{i}", text=text, section="Учёт в лаборатории", source_id=None, location=f"строка {i}")


class CoverageReviewTests(unittest.TestCase):
    def setUp(self):
        self.parts = [block(1, "Экран читает сохранённую маркировку пробирки."),
                      block(2, "До первой записи маркировка не назначена."),
                      block(3, "Раз в сутки разрешён один повторный отбор образца.")]
        self.blocks = {b.id: b for b in self.parts}
        self.claims = [dict(id="R" + b.id, block=b.id, quote=b.text, summary=b.text) for b in self.parts]
        self.axes = {"граница наблюдения": ["RB1", "RB2", "RB3"]}
        self.prior = engine._finding(
            dict(kind="Предполагаемый пробел", category="Полнота", severity="Существенная",
                 topic="Чтение маркировки", question="Как прочитать ранее сохранённую маркировку?",
                 test="Записать маркировку, прочитать и сравнить её с сохранённой.", scenario="Чтение образца.",
                 consequence="Неизвестен маршрут чтения.", reason="Задан экран с маркировкой.",
                 evidence=[dict(id="RB1", quote=self.parts[0].text)], reference="", interpretations=[], blocking=False, fix=""),
            {c["id"]: c for c in self.claims}, self.blocks, {})
        self.prior["id"] = "Z-008"

    def row(self, key, status, owner, *ident):
        return dict(key=key, axis="граница наблюдения", status=status, owner=owner, checked=list(ident),
                    decision=f"Решение по {key}", known="Задан тест для ранее сохранённой маркировки.",
                    distinction="Ответ о прочтении существующей записи не задаёт результат при её отсутствии.")

    def change(self, key, number, question):
        return dict(key=key, topic="Сверка " + key, category="Полнота", severity="Существенная",
                    question=question, test=f"Проверить состояние по решению {key}.",
                    outcomes=["В журнале отмечена проба.", "В журнале нет отметки."],
                    evidence=[dict(id=f"RB{number}", quote=self.parts[number-1].text)])

    def run_matrix(self, matrix, changes):
        return _reconcile(dict(matrix=matrix, changes=changes), self.axes, [self.prior], self.claims, self.blocks, {})

    def test_partial_coverage_extends_the_existing_owner_and_keeps_an_independent_decision(self):
        saved = deepcopy(self.prior)
        extension = self.change("absent", 2, "Как экран определяет результат до первой записи?")
        addition = self.change("day", 3, "По какому событию определяются сутки повторного отбора?")
        rows = [self.row("saved", "уже проверено", "Z-008", "RB1"),
                self.row("absent", "дополнить", "Z-008", "RB1", "RB2"),
                self.row("day", "новое решение", "", "RB3")]
        candidates, matrix = self.run_matrix(rows, [extension, addition])
        self.assertEqual(self.prior, saved)
        self.assertEqual([f["id"] for f in candidates], ["Z-008", "Z-009"])
        self.assertEqual([r["finding_id"] for r in matrix], ["Z-008", "Z-008", "Z-009"])
        self.assertEqual(matrix[1]["outcomes"], extension["outcomes"])
        self.assertEqual(candidates[0]["ids"], ["RB1", "RB2"])
        self.assertIn(saved["question"], candidates[0]["question"])
        self.assertIn(extension["test"], candidates[0]["test"])
        self.assertFalse(candidates[1]["counted"])
        json.dumps(matrix)

    def test_does_not_multiply_the_same_observable_decision(self):
        duplicate = self.change("duplicate", 1, self.prior["question"])
        duplicate["test"] = self.prior["test"]
        candidates, matrix = self.run_matrix([self.row("duplicate", "новое решение", "Z-008", "RB1")], [duplicate])
        self.assertEqual(candidates, [self.prior])
        self.assertEqual(matrix[0]["finding_id"], self.prior["id"])

    def test_solved_rows_produce_no_question(self):
        candidates, matrix = self.run_matrix([self.row("settled", "задано", "", "RB2")], [])
        self.assertEqual(candidates, [self.prior])
        self.assertEqual(matrix[0]["finding_id"], "")

    def test_unknown_owner_false_quote_or_missing_observable_alternative_is_rejected(self):
        row = self.row("gap","новое решение","","RB3")
        change = self.change("gap",3,"Когда начинаются сутки?")
        for invalid_row, invalid_change in [
            (dict(row,owner="Z-009"), change),
            (dict(row,checked=["RB1"]), change),
            (row, dict(change,evidence=[dict(id="RB3",quote="В полночь") ])),
            (row, dict(change,outcomes=["Одинаково", "Одинаково"])),
        ]:
            with self.subTest(row=invalid_row, change=invalid_change), self.assertRaises(ValueError):
                self.run_matrix([invalid_row], [invalid_change])

    def test_small_document_makes_no_additional_provider_request(self):
        candidates, matrix = supplement(None, self.claims, self.blocks, [self.prior], {}, "", self.fail)
        self.assertEqual(candidates, [self.prior])
        self.assertEqual(matrix, [])

    def test_full_document_pass_checks_each_detected_axis_and_preserves_settled_results(self):
        parts = [block(i, f"Клиент читает запись {i} раз в сутки. При отсутствии записи возвращается пустой ответ.")
                 for i in range(1, 51)]
        blocks = {b.id:b for b in parts}
        claims = [dict(id="R" + b.id, block=b.id, quote=b.text, summary=b.text) for b in parts]
        calls = []
        class Settled:
            def ask(self, prompt, schema):
                data = json.loads(prompt.split("Вход (JSON):\n", 1)[1])
                calls.append(data)
                return dict(matrix=[dict(key=str(i), axis=axis, checked=[ids[0]], decision="Чтение записи.",
                                         status="задано", owner="", known="При отсутствии выдаётся пустой ответ.",
                                         distinction="") for i,(axis,ids) in enumerate(data["axes"].items())],
                            changes=[])
        candidates, matrix = supplement(Settled(), claims, blocks, [], {}, "", lambda _:None)
        self.assertEqual(candidates, [])
        self.assertEqual(len(calls), 1)
        self.assertEqual({r["axis"] for r in matrix}, calls[0]["axes"].keys())
        self.assertEqual(len(calls[0]["claims"]), 50)
