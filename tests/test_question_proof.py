import unittest

from requirements_validator.question_proof import apply_revisions


class QuestionProofTests(unittest.TestCase):
    def setUp(self):
        self.raw = {"decisions": [{"id": "Z-002", "action": "оставить", "question_mode": "сохранить",
                                   "question_check": [{"obligation_id": "R-1", "decision": "Выбрать путь."}]}]}
        self.accepted = [{"id": "Z-002", "question": "Как получить данные?"}]
        self.edit = {"id": "Z-002", "question": "Откуда экран читает данные до первой записи?",
                     "test": "Открыть новый экран и проверить значение.", "decision": "Указать источник.",
                     "outcomes": ["Значение предоставил каталог.", "Значение предоставил сервис."]}

    def test_only_wording_and_acceptance_details_can_be_revised(self):
        result = apply_revisions([self.edit], self.raw, self.accepted, lambda data: data)
        revised = result["decisions"][0]
        self.assertEqual(revised["question"], self.edit["question"])
        self.assertEqual(revised["question_check"][0]["obligation_id"], "R-1")
        self.assertEqual(revised["action"], "оставить")
        self.assertEqual(self.raw["decisions"][0]["question_mode"], "сохранить")

    def test_revision_cannot_add_or_duplicate_a_finding(self):
        for edits in ([dict(self.edit, id="Z-999")], [self.edit, self.edit]):
            with self.subTest(edits=edits), self.assertRaises(ValueError):
                apply_revisions(edits, self.raw, self.accepted, lambda data: data)

    def test_edited_verdict_must_pass_the_original_validator(self):
        def reject(data):
            raise ValueError("Неподтверждённая предпосылка")

        with self.assertRaisesRegex(ValueError, "Неподтверждённая"):
            apply_revisions([self.edit], self.raw, self.accepted, reject)
