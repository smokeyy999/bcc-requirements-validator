import unittest

from requirements_validator.engine import _adjudicate_one


class QuestionCategoryTests(unittest.TestCase):
    def test_review_keeps_the_quality_category_when_the_question_has_the_same_basis(self):
        examples = {
            "Проверяемость": ("Тепловое реле должно сработать оперативно.",
                              "Какой интервал срабатывания считать приемлемым?"),
            "Ясность": ("Оператор выбирает штатный профиль.",
                        "Как распознать штатный профиль?"),
            "Трассируемость": ("Сигнал описан в приложении К.",
                               "Где доступно упомянутое приложение К?"),
        }
        for category, (quote, question) in examples.items():
            with self.subTest(category=category):
                item = dict(kind="Дефект", category=category, counted=True,
                            ids=["R-X-01"], evidence=[{"id": "R-X-01", "quote": quote}])
                decision = dict(action="уточнить", basis="Обоснованное ожидание", severity="Низкая",
                                blocking=False, question_mode="заменить", question=question,
                                reason=quote, test="Зафиксировать ответ в сценарии испытания.",
                                supports=["R-X-01"], case_check={"status": "не применимо", "anchors": [],
                                                                "condition": "", "effect": ""})
                reviewed = _adjudicate_one(decision, item)
                self.assertEqual((reviewed["kind"], reviewed["category"]), ("Предполагаемый пробел", category))
                self.assertFalse(reviewed["counted"] or reviewed["blocking"])

    def test_question_about_an_unproved_condition_replaces_the_original_diagnosis(self):
        quote = {"id": "R-X-01", "quote": "В ускоренном режиме используется особый профиль."}
        item = dict(kind="Дефект", category="Ясность", counted=True, ids=["R-X-01"], evidence=[quote])
        decision = dict(action="уточнить", basis="Обоснованное ожидание", severity="Низкая",
                        blocking=False, question_mode="заменить", question="Включён ли ускоренный режим?",
                        reason="Режим в испытании не задан.", test="Сначала сверить режим.",
                        supports=["R-X-01"], case_check={"status": "требует ответа", "anchors": [quote],
                            "condition": "Режим не указан.",
                            "effect": "При ускоренном режиме проверяют особый профиль, иначе он не требуется."})
        reviewed = _adjudicate_one(decision, item)
        self.assertEqual(reviewed["category"], "Полнота")
        self.assertFalse(reviewed["counted"] or reviewed["blocking"])
