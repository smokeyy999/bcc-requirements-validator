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

    def test_reopening_requires_an_existing_decision_under_review_and_a_new_summary(self):
        previous = {"decisions": [{"id": "Z-002", "action": "снять", "question_mode": "убрать",
                                   "question_check": [], "same_decision_as": ""}]}
        replacement = dict(previous["decisions"][0], action="оставить", question_mode="сохранить")
        summary = {"assessment": "Остался один вопрос.", "readiness": "Требуется согласование.",
                   "priorities": [{"ids": ["Z-002"], "step": "Уточнить источник."}]}
        with self.assertRaises(ValueError):
            apply_revisions([], previous, [], lambda x: x, reopen=[replacement], summaries=[summary])
        with self.assertRaises(ValueError):
            apply_revisions([], previous, [], lambda x: x, reopen=[replacement], allowed_reopen={"Z-002"})
        result = apply_revisions([], previous, [], lambda x: x, reopen=[replacement],
                                 allowed_reopen={"Z-002"}, summaries=[summary])
        self.assertEqual(result["decisions"][0]["action"], "оставить")
        self.assertEqual(previous["decisions"][0]["action"], "снять")

    def test_empty_queue_still_reviews_why_an_open_case_disappeared(self):
        from requirements_validator import engine

        quote = "При первом открытии каталог возвращает пустой список."
        matrix = [dict(key="first", finding_id="Z-002", status="новое решение", decision="Экран до заполнения каталога",
                       known="Каталог отдаёт данные экрану.", distinction="Первое открытие.",
                       checked=["R-1"], question="Что вернёт каталог?", test="Проверить первое открытие.",
                       outcomes=["Пустой список.", "Ошибка чтения."])]
        raw = {"decisions": [dict(id="Z-002", action="снять", same_decision_as="", reason="Ответ описан.")]}
        audit = dict(blocks=[], candidates=[{"id": "Z-002"}], claims=[dict(id="R-1", quote=quote)])
        class Provider:
            def ask(self, prompt, schema):
                self.schema = schema
                return dict(edits=[], reopened=[], summary=[], dispositions=[
                    dict(key="first", status="закрыто", owner="", question_quote="", test_quote="",
                         source_id="R-1", source_quote="каталог возвращает пустой список",
                         reason="Для первого открытия результат чтения каталога уже задан как пустой список.")])
        provider = Provider()
        reviewed = ([], {}, {})
        result = engine._proofread_questions(provider, matrix, raw, reviewed, [], audit,
                                             lambda decision: reviewed, lambda msg: None)
        self.assertEqual(result, reviewed)
        self.assertIs(provider.schema, engine.HANDOFF_EDITS)
        self.assertEqual(matrix[0]["final_check"]["source_id"], "R-1")
