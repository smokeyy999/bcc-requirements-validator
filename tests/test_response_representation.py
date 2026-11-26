import unittest
from types import SimpleNamespace

from requirements_validator.response_representation import representation_error, response_obligations


RULE = "При отклонении редакции вернуть прежний профиль и результат ERROR."
QUESTION = "В каких полях ответа передаётся прежний профиль при отклонении редакции?"
TEST = ("Установить известный профиль, отклонить его замену, извлечь значения из полей "
        "ответа и сравнить с прежним профилем.")
OUTCOMES = ["Прежний профиль находится во вложенном объекте.",
            "Тот же профиль доступен в отдельных полях ответа."]


def issue(question=QUESTION, test=TEST, rules=(RULE,), outcomes=OUTCOMES, options=()):
    source = {str(i): rule for i, rule in enumerate(rules)}
    finding = dict(ids=list(source), question=question, test=test,
                   proposal_options=[dict(effect=option) for option in options],
                   question_basis=dict(checked_ids=list(source), outcomes=outcomes))
    return representation_error(finding, finding, source)


class ReturnedStateTests(unittest.TestCase):
    def test_only_direct_return_activates_the_instruction(self):
        lines = [RULE, "При отказе сохранить прежний профиль и вернуть код ошибки.",
                 "При отказе вернуть прежний профиль в хранилище, выдать клиенту ошибку.",
                 "При отказе можно вернуть прежний профиль клиенту.",
                 "On failure, do not return the previous profile to the caller.",
                 "On failure return the previous profile to the caller."]
        blocks = [SimpleNamespace(id=i, text=line) for i, line in enumerate(lines)]
        self.assertEqual(response_obligations(blocks), [0, 5])

    def test_a_storage_interpretation_cannot_remove_the_returned_value(self):
        wide = "Обязано ли тело ответа при отклонении содержать прежние настройки?"
        self.assertIn("представлением", issue(wide))
        self.assertIn("представлением", issue(outcomes=["Ответ содержит прежние данные.",
                                                        "Ответ без прежних данных проходит проверку."]))
        self.assertIn("представлением", issue(options=["При отказе настройка остаётся только в хранилище."]))

    def test_narrow_question_needs_an_observation_in_the_returned_payload(self):
        self.assertEqual(issue(), "")
        self.assertIn("сверь", issue(test="Отклонить редакцию и проверить прежние значения в базе."))
        question = "Можно ли вернуть прежние значения во вложенном объекте или требуются отдельные поля?"
        self.assertEqual(issue(question), "")

    def test_persistence_and_other_error_fields_remain_independent(self):
        wide = "Нужно ли возвращать клиенту прежние настройки при отказе?"
        self.assertEqual(issue(wide, rules=["При отказе сохранить прежние настройки и вернуть ошибку."]), "")
        self.assertEqual(issue("Какие поля статуса и сообщения обязательны для отказа в доступе?"), "")
        conflict = "При отклонении редакции не возвращать прежний профиль клиенту."
        self.assertEqual(issue(wide, rules=[RULE, conflict]), "")

    def test_reference_to_the_original_values_at_the_comparison_step(self):
        self.assertEqual(issue(test="Для клиента с сохранёнными настройками отклонить запись. "
                               "Считать обе настройки из тела ответа и сверить их с исходными."), "")

    def test_an_explicit_field_only_resolves_its_own_name(self):
        fixed = "При отклонении редакции вернуть прежний профиль в поле `snapshot` и результат ERROR."
        field = "В каком поле ответа передаётся прежний профиль?"
        self.assertIn("прямо названо поле", issue(field, rules=[fixed]))
        self.assertEqual(issue("Какова структура прежнего профиля внутри поля snapshot?", rules=[fixed]), "")
        other = "При отклонении редакции вернуть прежний профиль и код ошибки в поле `code`."
        self.assertEqual(issue(field, rules=[other]), "")

    def test_missing_values_may_legitimately_fail_the_acceptance_test(self):
        self.assertEqual(issue(outcomes=["Тело без прежних данных не проходит проверку.",
                                         "Все прежние значения переданы в согласованных полях."]), "")
