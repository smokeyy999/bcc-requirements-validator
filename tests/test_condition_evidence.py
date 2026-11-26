import unittest

from requirements_validator.condition_evidence import direct_condition_evidence
from requirements_validator.engine import _final_decisions
from requirements_validator.report import question_basis
from tests.test_engine import checked_question


class ConditionEvidenceTests(unittest.TestCase):
    def base(self, question, other, general="Сервис выполняет проверку введённых данных."):
        own, context = "R-A-01", "R-B-01"
        quotes = {own: general, context: other}
        proof, = checked_question(own, general, question, "Результат сохранён.", "Результат возвращён.",
                                  state="не задан результат действия")
        finding = dict(id="Z-001", kind="Дефект", category="Полнота", counted=True, blocking=False,
                       ids=[own, context], evidence=[dict(id=k, quote=v) for k, v in quotes.items()],
                       question=question, test=question, scenario=question, topic="Результат обработки",
                       reason="Нужен ожидаемый результат.", fix="", question_basis=proof)
        return finding, quotes

    def test_valid_and_invalid_direction_preserve_context_and_archived_evidence(self):
        examples = [
            ("Что происходит для корректных показаний?", "При получении некорректного значения выводится отказ."),
            ("Какой ответ требуется для невалидного ввода?", "Для валидного ввода сервис выдаёт подтверждение."),
            ("Как должна обрабатываться активная подписка?", "При неактивной подписке доступ закрыт."),
            ("Как обслуживается неактивная подписка?", "При активной подписке доступ открыт."),
            ("What must a connected device show?", "When the device is disconnected, display a banner."),
            ("What must a disconnected device show?", "When the device is connected, display the current count."),
        ]
        for question, other in examples:
            with self.subTest(question=question):
                finding, quotes = self.base(question, other)
                updated = direct_condition_evidence(finding, quotes)
                self.assertEqual(updated["ids"], ["R-A-01"])
                self.assertEqual([e["id"] for e in updated["evidence"]], updated["ids"])
                self.assertIn("R-B-01", updated["question_basis"]["checked_ids"])
                self.assertIn("[R-B-01]", " ".join(question_basis(updated)))
                self.assertEqual(finding["ids"], ["R-A-01", "R-B-01"])

    def test_mixed_conditions_different_entities_and_output_labels_remain_direct(self):
        examples = [
            ("Which outcome applies to a valid input?", "For an invalid input reject it, otherwise return success."),
            ("Какая реакция ожидается для корректных данных?", "Для некорректных данных выдать отказ. Всегда записывать попытку."),
            ("Как обслуживать активную подписку?", "При неактивном аккаунте остановить платёж."),
            ("Which outcome applies to a valid value of field firstName?", "For an invalid value of field lastName, reject the update."),
            ("Which result applies to a valid input?", "The audit records every invalid input."),
            ("Что требуется для корректного и некорректного ввода?", "Для некорректного ввода показать сообщение."),
            ("Что требуется для активной подписки?", "Для активной подписки доступ запрещён."),
            ("What must a connected device show?", "If connected and disconnected devices are present, show a list."),
        ]
        for question, other in examples:
            with self.subTest(other=other):
                finding, quotes = self.base(question, other)
                self.assertIs(direct_condition_evidence(finding, quotes), finding)

    def test_never_removes_the_only_obligation_comparisons_or_genuine_conflict(self):
        finding, quotes = self.base("Что делать для валидного ввода?", "Для невалидного ввода вернуть ошибку.")
        cases = [
            dict(ids=["R-B-01"]), dict(kind="Дефект", category="Противоречивость"),
            dict(kind="Неоднозначность"), dict(proposal_options=[{"anchor": finding["evidence"][1]}]),
            dict(question_basis=dict(finding["question_basis"], obligation_id="R-B-01")),
            dict(scenario="Сравнить результаты для валидного и невалидного ввода."),
        ]
        for changes in cases:
            changed = dict(finding, **changes)
            with self.subTest(changes=changes):
                self.assertIs(direct_condition_evidence(changed, quotes), changed)

    def test_normal_adjudication_keeps_checked_context_in_published_basis(self):
        finding, quotes = self.base("Какой результат обязателен для валидного ввода?",
                                    "Для невалидного ввода вернуть ошибку.")
        proof = finding.pop("question_basis")
        verdict = dict(id="Z-001", action="оставить", basis="Прямое обязательство", severity="Существенная",
                       blocking=False, reason="Требуемый ответ открыт.", supports=[], same_decision_as="",
                       question_mode="сохранить", question="", test="", question_check=[proof],
                       case_check=dict(status="не применимо", anchors=[], condition="", effect=""))
        raw = dict(assessment="Рассмотрено.", readiness="Нужен ответ.", decisions=[verdict],
                   priorities=[dict(ids=["Z-001"], step="Согласовать результат.")])
        result, _, _ = _final_decisions(raw, [finding], [dict(id=k, quote=v) for k, v in quotes.items()])
        self.assertEqual(result[0]["ids"], ["R-A-01"])
        self.assertIn("R-B-01", result[0]["question_basis"]["checked_ids"])
