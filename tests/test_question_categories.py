import unittest

from requirements_validator.engine import _adjudicate_one, _final_decisions, _questions
from requirements_validator.report import question_basis
from tests.test_engine import checked_question


class QuestionCategoryTests(unittest.TestCase):
    def setUp(self):
        self.rule = {"id": "R-X-01", "quote": "Приёмка включает калибровку светильника."}
        self.coverage = {"id": "R-X-02", "quote": "Контрольные цвета будут согласованы отдельно."}
        self.claims = [self.rule, self.coverage]
        self.item = dict(id="Z-001", kind="Дефект", category="Проверяемость", counted=True,
                         ids=[self.rule["id"]], evidence=[self.rule], question="Какие цвета проверить?",
                         reason="Состав калибровки открыт.", test="Пройти калибровку.",
                         fix="", topic="Калибровка")
        self.check = checked_question(self.rule["id"], self.rule["quote"], self.item["question"],
            "Один измеренный цвет завершает испытание.", "Требуется проверить ещё один цвет.",
            state="неполный приёмочный сценарий")[0]
        self.check["checked_ids"].append(self.coverage["id"])
        self.decision = dict(id="Z-001", action="оставить", basis="Прямое обязательство",
            severity="Существенная", blocking=False, supports=[], question_mode="сохранить",
            question="", test="", reason=self.item["reason"], question_check=[self.check],
            same_decision_as="", case_check=dict(status="не применимо", condition="", anchors=[], effect=""))

    def reviewed(self, **changes):
        return _adjudicate_one(dict(self.decision, **changes), self.item,
                               {c["id"]: c["quote"] for c in self.claims})

    def test_missing_promised_acceptance_step_differs_from_a_missing_measure(self):
        reviewed = self.reviewed()
        self.assertTrue(reviewed["counted"])
        self.assertEqual(reviewed["category"], "Полнота")
        self.assertEqual(reviewed["question_basis"]["checked_ids"], ["R-X-01", "R-X-02"])
        self.rule["quote"] = "Светильник обеспечивает комфортный свет."
        self.check.update(state="нет меры заявленного свойства", known_answer=self.rule["quote"],
                          decision="Какая освещённость считается комфортной?")
        self.item["category"] = "Полнота"
        self.check["outcomes"] = ["Замер проходит по заданной границе.", "Тот же замер вне принятой границы."]
        self.assertEqual(self.reviewed()["category"], "Проверяемость")

    def test_open_question_requires_a_sourced_independent_decision_and_different_outcomes(self):
        self.item.update(kind="Предполагаемый пробел", counted=False)
        with self.assertRaisesRegex(ValueError, "проверка вопроса"):
            self.reviewed(question_check=[])
        for changes in ({"obligation_id": "R-X-99"}, {"checked_ids": ["R-X-99"]}, {"checked_ids": []},
                        {"decision": ""}, {"known_answer": ""}, {"outcomes": ["Экран светится.", "Экран светится!"]},
                        {"state": "ответ дан"}, {"state": "необязательная деталь"},
                        {"state": "зависит от другого решения"}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.reviewed(question_check=[dict(self.check, **changes)])
        self.assertEqual(self.reviewed()["question"], self.item["question"])

    def test_report_shows_partial_answer_sources_and_outcomes_without_repeating_the_question(self):
        reviewed = self.reviewed()
        details = "\n".join(question_basis(reviewed))
        self.assertNotIn(self.item["question"], details)
        for text in (self.rule["quote"], *self.check["outcomes"], "[R-X-02](#r-x-02)"):
            self.assertIn(text, details)
        reviewed["consequence"] = self.check["outcomes"][0]
        self.assertNotIn(self.check["outcomes"][0], "\n".join(question_basis(reviewed)))

    def test_explicit_shared_decision_collects_tests_but_keeps_independent_questions(self):
        second = dict(self.item, id="Z-002", question="Какой набор цветов считать достаточным?",
                      test="Повторить калибровку после смены питания.")
        third = dict(self.item, id="Z-003", question="Какой режим выбрать для проверки цвета?",
                     test="Повторить калибровку на штатной яркости.")
        decisions = [self.decision, dict(self.decision, id=second["id"], same_decision_as=self.item["id"]),
                     dict(self.decision, id=third["id"])]
        audit = dict(decisions=decisions, priorities=[dict(ids=[self.item["id"]], step="Согласовать испытания.")],
                     assessment="Состав проверки открыт.", readiness="Согласовать приёмку.")
        findings, _, _ = _final_decisions(audit, [self.item, second, third], self.claims)
        queue = _questions(findings)
        self.assertEqual(len(queue), 2)
        self.assertEqual(queue[0]["findings"], ["Z-001", "Z-002"])
        self.assertIn(second["test"], queue[0]["test"])
        self.assertEqual(queue[1]["findings"], ["Z-003"])
        for invalid in ("Z-002", "Z-999"):
            decisions[1]["same_decision_as"] = invalid
            with self.subTest(invalid=invalid), self.assertRaisesRegex(ValueError, "same_decision_as"):
                _final_decisions(audit, [self.item, second, third], self.claims)

    def test_dismissed_duplicate_keeps_the_additional_citation_on_the_surviving_card(self):
        duplicate = dict(self.item, id="Z-002", ids=[self.coverage["id"]], evidence=[self.coverage])
        removed = dict(self.decision, id=duplicate["id"], action="снять", question_mode="убрать",
                       same_decision_as=self.item["id"], question_check=[])
        audit = dict(decisions=[self.decision, removed],
                     priorities=[dict(ids=[self.item["id"]], step="Согласовать испытания.")],
                     assessment="Одна незакрытая проверка.", readiness="Нужно определить цвета.")
        findings, _, _ = _final_decisions(audit, [self.item, duplicate], self.claims)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["ids"], [self.rule["id"], self.coverage["id"]])
        self.assertEqual(findings[0]["evidence"], self.claims)

    def test_corrected_test_replaces_the_original_wrong_scenario(self):
        self.item["scenario"] = "Проверить длительность одного заполнения."
        corrected = "Сложить длительности всех заполнений за смену и сравнить итог со сроком."
        reviewed = self.reviewed(question_mode="заменить", question=self.item["question"], test=corrected)
        self.assertEqual(reviewed["scenario"], corrected)
        self.assertEqual(reviewed["test"], corrected)

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
                                question_check=checked_question("R-X-01", quote, question,
                                    "Результат укладывается в выбранный критерий.",
                                    "Для этого же наблюдения критерий не выполнен."),
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
                        question_check=checked_question("R-X-01", quote["quote"],
                            "Какой режим принят для испытания?", "Проверяют особый профиль.",
                            "Проверяют основной профиль."),
                        supports=["R-X-01"], case_check={"status": "требует ответа", "anchors": [quote],
                            "condition": "Режим не указан.",
                            "effect": "При ускоренном режиме проверяют особый профиль, иначе он не требуется."})
        reviewed = _adjudicate_one(decision, item)
        self.assertEqual(reviewed["category"], "Полнота")
        self.assertFalse(reviewed["counted"] or reviewed["blocking"])
