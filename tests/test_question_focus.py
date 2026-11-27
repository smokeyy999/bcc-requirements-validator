import unittest

from requirements_validator.engine import _final_decisions, DraftError
from requirements_validator.question_focus import question_focus_error
from tests.test_engine import checked_question


class QuestionFocusTests(unittest.TestCase):
    def finding(self, question, known="", outcomes=(), reason="", test="Проверить ответ."):
        return dict(question=question, ids=["R-1"], reason=reason, test=test,
                    question_basis=dict(checked_ids=["R-1"], known_answer=known,
                                        decision=question, outcomes=list(outcomes)))

    def test_initial_absence_needs_its_own_evidence(self):
        question = "В каких полях ответ передаёт прежнее состояние?"
        finding = self.finding(question, "До первого сохранения звонок выключен, а лимита нет.")
        evidence = {"R-1": "По умолчанию звонок выключен."}
        self.assertIn("Начальное значение", question_focus_error(finding, evidence))
        evidence["R-2"] = "До первого сохранения идентификатора нет."
        finding["question_basis"]["checked_ids"].append("R-2")
        self.assertIn("Начальное значение", question_focus_error(finding, evidence))
        evidence["R-2"] = "До первого сохранения лимит отсутствует."
        self.assertEqual(question_focus_error(finding, evidence), "")

    def test_fixture_and_open_choice_do_not_claim_a_universal_default(self):
        question = "Что показывает клиент до первого сохранения: отсутствие лимита или исходную сумму?"
        fixture = "Для теста подготовить устройство без записи. Сравнить ответ с подготовленным состоянием."
        finding = self.finding(question, "По умолчанию звонок выключен.", test=fixture)
        self.assertEqual(question_focus_error(finding, {"R-1": "По умолчанию звонок выключен."}), "")
        finding["question"] = "Как до первого сохранения приложение отображает отсутствие лимита?"
        self.assertIn("Начальное значение", question_focus_error(finding, {"R-1": "По умолчанию звонок выключен."}))

    def test_range_minimum_is_not_a_default(self):
        finding = self.finding("Как ответ передаёт исходное состояние?", "По умолчанию лимит 1000.")
        evidence = {"R-1": "По умолчанию звонок выключен. Лимит от 1 000 до 1 000 000."}
        self.assertIn("Начальное значение", question_focus_error(finding, evidence))
        evidence["R-1"] += " Лимит по умолчанию равен 1 000."
        self.assertEqual(question_focus_error(finding, evidence), "")
        finding["question_basis"]["known_answer"] = "До первого сохранения лимит равен 2 000."
        self.assertIn("Начальное значение", question_focus_error(finding, evidence))
        finding["question_basis"]["known_answer"] = "По умолчанию звонок выключен."
        finding["test"] = "Подготовить запись с лимитом 2 000 и сравнить ответ с ней."
        self.assertEqual(question_focus_error(finding, evidence), "")

    def test_missing_initial_evidence_and_decimal_default(self):
        finding = self.finding("Как читать значение?", "По умолчанию лимит 2.5.")
        evidence = {"R-1": "Установить лимит от 2.5 до 5."}
        self.assertIn("Начальное значение", question_focus_error(finding, evidence))
        finding["question_basis"]["known_answer"] = "До первого сохранения лимита нет."
        self.assertIn("Начальное значение", question_focus_error(finding, evidence))
        finding["question_basis"]["known_answer"] = "По умолчанию лимит 2.5."
        evidence["R-1"] += " Лимит по умолчанию равен 2.8."
        self.assertIn("Начальное значение", question_focus_error(finding, evidence))
        finding["question_basis"]["known_answer"] = "По умолчанию лимит 2,8."
        self.assertEqual(question_focus_error(finding, evidence), "")

    def test_equivalent_routes_and_distinct_external_exchanges(self):
        question = "Откуда клиент получает deviceId выбранного устройства?"
        first = "Оба вызова передают deviceId из данных выбранного устройства."
        second = "Оба вызова передают deviceId, полученный для выбранного устройства из локального справочника."
        finding = self.finding(question, "В запросе обязателен deviceId.", [first, second])
        evidence = {"R-1": "В запросе обязателен deviceId выбранного устройства."}
        self.assertIn("внутренний маршрут", question_focus_error(finding, evidence))
        for outcome in [
            "Оба вызова передают deviceId через заголовок, обязательный для авторизации.",
            "Сервис отклоняет запрос для чужого устройства.",
            "Оба вызова передают deviceId из результата обязательного запроса GET /devices.",
        ]:
            with self.subTest(outcome=outcome):
                finding["question_basis"]["outcomes"] = [first, outcome]
                self.assertEqual(question_focus_error(finding, evidence), "")

    def test_wire_contract_and_initial_state_have_different_owners(self):
        question = ("Какой запрос выполняет клиент и из каких полей он читает результат после замены? "
                    "Что получает приложение до первой записи?")
        issue = question_focus_error(self.finding(question), {})
        self.assertIn("один предмет решения", issue)
        test = "Открыть экран до первой записи. После замены прочитать новые значения обоих полей."
        focused = "Какие поля возвращает чтение записанных настроек?"
        self.assertEqual(question_focus_error(self.finding(focused, test=test), {}), "")
        self.assertEqual(question_focus_error(self.finding("Включать ли архив? Если да, как его читать?"), {}), "")

    def test_final_decisions_requests_repair_at_the_question_and_evidence(self):
        ident = "R-X-01"
        rule = dict(id=ident, quote="По умолчанию звонок выключен.")
        question = "В каких полях ответ передаёт прежнее состояние?"
        item = dict(id="Z-001", kind="Предполагаемый пробел", category="Полнота", counted=False,
                    ids=[ident], evidence=[rule], question=question, test="Сверить поля ответа.", fix="")
        check = checked_question(ident, "До первого сохранения звонок выключен, а лимита нет.",
                                 question, "В одном поле.", "В двух полях.")
        decision = dict(id="Z-001", action="оставить", basis="Обоснованное ожидание", severity="Существенная",
                        blocking=False, supports=[], question_mode="сохранить", question="", test="",
                        reason="Состав ответа открыт.", question_check=check, same_decision_as="",
                        case_check=dict(status="не применимо", condition="", anchors=[], effect=""))
        audit = dict(decisions=[decision], assessment="Описание доступно.", readiness="Нужно решение.",
                     priorities=[dict(step="Уточнить поля.", ids=["Z-001"])])
        with self.assertRaisesRegex(DraftError, "Начальное значение") as err:
            _final_decisions(audit, [item], [rule])
        self.assertIn("/decisions/0", err.exception.paths)
        self.assertIn("/decisions/0/question_check", str(err.exception))
        check[0]["known_answer"] = "По умолчанию звонок выключен."
        findings, _, _ = _final_decisions(audit, [item], [rule])
        self.assertEqual([f["question"] for f in findings], [question])
