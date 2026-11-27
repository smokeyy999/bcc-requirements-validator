import unittest
from types import SimpleNamespace

from requirements_validator.deferred_acceptance import diagnosis, linked, missing, promised_procedures


def inspect(*items):
    blocks, claims = [], []
    for i, item in enumerate(items, 1):
        section, text = item if isinstance(item, tuple) else ("Правила", item)
        block = SimpleNamespace(id=f"B{i}", section=section, text=text)
        blocks.append(block)
        claims.append(dict(id=f"R{i}", block=block.id, quote=text))
    return promised_procedures(blocks, claims)


PROMISE = ('На стенде обязательна проверка кнопки «Архивировать». '
           'Приёмочное испытание будет определено позже.')
RULE = 'В редакторе после нажатия «Архивировать» карточка переходит в архив.'


class DeferredAcceptanceTest(unittest.TestCase):
    def test_normal_operation_is_not_the_promised_acceptance_case(self):
        obligation, = inspect(PROMISE, RULE)
        self.assertEqual(obligation["subject"], "Архивировать")
        self.assertEqual(obligation["claims"], ["R1"])
        self.assertEqual(obligation["missing_parts"], ["шаг испытания", "наблюдаемый результат"])
        self.assertIn(obligation["subject"], diagnosis(obligation))
        self.assertTrue(missing(obligation, []))

    def test_concrete_example_elsewhere_can_supply_both_parts_without_acceptance_label(self):
        example = ('Пример. В редакторе нажать «Архивировать». '
                   'Тогда карточка отображается только в архиве.')
        self.assertFalse(inspect(PROMISE, RULE, ("Примеры редактора", example)))
        self.assertFalse(inspect(PROMISE, RULE, ("Сценарий «Архивировать»", "Шаг 1: открыть карточку."),
                                 ("Сценарий «Архивировать»", "Ожидаемый результат: карточка в архиве.")))
        self.assertFalse(inspect(PROMISE, RULE, 'Когда оператор нажимает «Архивировать», тогда карточка в архиве.'))

    def test_only_unresolved_part_is_signalled(self):
        step, = inspect(PROMISE, ("Сценарий «Архивировать»", "Шаг 1: открыть карточку."))
        self.assertEqual(step["missing_parts"], ["наблюдаемый результат"])
        effect, = inspect(PROMISE, ("Сценарий «Архивировать»", "Ожидаемый результат: запись в архиве."))
        self.assertEqual(effect["missing_parts"], ["шаг испытания"])
        partial, = inspect(PROMISE, ("Сценарий «Архивировать»", "Шаг 1: открыть карточку."),
                           ("Сценарий «Архивировать»", "Ожидаемый результат пока не определён."))
        self.assertEqual(partial["missing_parts"], ["наблюдаемый результат"])

    def test_do_not_borrow_a_test_for_another_action_or_incompatible_state(self):
        qualified = PROMISE.replace('«Архивировать»', '«Архивировать» в состоянии «Черновик»')
        for name, state in [("Удалить", "Черновик"), ("Архивировать", "Опубликовано")]:
            example = f'Пример: в состоянии «{state}» нажать «{name}». Ожидаемый результат: карточка в архиве.'
            self.assertTrue(inspect(qualified, example), example)
        self.assertTrue(inspect(qualified, example.replace("карточка в архиве", "состояние «Черновик»")))
        self.assertFalse(inspect(qualified, example.replace("Опубликовано", "Черновик")))

    def test_subject_in_another_example_or_its_expected_output_is_not_the_action_under_test(self):
        for body in (RULE + " Пример: нажать «Удалить». Ожидаемый результат: корзина пуста.",
                     "Пример: нажать «Удалить». Тогда на экране отображается кнопка «Архивировать»."):
            with self.subTest(body=body):
                gap, = inspect(PROMISE, body)
                self.assertEqual(gap["missing_parts"], ["шаг испытания", "наблюдаемый результат"])

    def test_do_not_require_a_test_type_by_default_or_if_only_the_date_is_deferred(self):
        for source in (RULE, "Приёмочное испытание будет определено позже.",
                       "Предусмотрен тест кнопки «Анализ». Дата приёмочного испытания будет определена позже.",
                       "При необходимости приёмочный тест команды «Анализ» будет определён позднее.",
                       "Функция «Анализ» будет определена позже. Для неё предусмотрена проверка.",
                       "Обязательна проверка кнопки «Анализ». Приёмочное испытание будет проведено позже."):
            self.assertFalse(inspect(source), source)
        self.assertFalse(inspect("На стенде обязательна проверка кнопки «Архивировать».", RULE,
                                 "Приёмочное испытание будет определено позже."))

    def test_unquoted_operations_and_separate_adjacent_promise(self):
        rule = "Обязательна проверка экспорта данных."
        item, = inspect(rule, "Процедура приёмки будет описана позднее.")
        self.assertEqual(item["subject"], "экспорта данных")
        self.assertEqual(item["claims"], ["R2", "R1"])
        self.assertFalse(inspect(rule, "Процедура приёмки будет описана позднее.",
                                 ("Пример экспорта данных", "Шаг: открыть форму."),
                                 ("Пример экспорта данных", "Ожидаемый результат: файл готов.")))

    def test_specific_confirmed_finding_required_on_same_obligation(self):
        obligation, = inspect(PROMISE)
        complete = dict(ids=["R1"], counted=True, kind="Дефект", category="Полнота",
                        topic="Не описан критерий приёмочного испытания")
        self.assertTrue(linked(obligation, complete))
        self.assertFalse(missing(obligation, [complete]))
        for change in (dict(counted=False), dict(ids=["R2"]), dict(category="Проверяемость"),
                       dict(topic="Не указано конечное состояние карточки"),
                       dict(topic="Без конечного состояния нельзя проверить работу команды")):
            self.assertTrue(missing(obligation, [{**complete, **change}]), change)


if __name__ == "__main__":
    unittest.main()
