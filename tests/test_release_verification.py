import unittest

from scripts.verify_release import verify_choices, verify_proposals


class ChoiceReadbackTests(unittest.TestCase):
    def test_each_option_requires_its_own_source_and_a_distinct_result(self):
        body = ('[R-D001-01](#r-d001-01) · [строка 5](source.md#L5)\n\n> Лампа горит  \n\n'
                '[R-D002-01](#r-d002-01) · [строка 7](source.md#L7)\n\n> Лампа мигает  \n\n')
        options = '''**Вопрос для решения.** Какой сигнал увидит оператор?

1. **Вариант 1.** Выбрать первый сигнал.
   **Основание.** [R-D001-01](#r-d001-01) «Лампа горит».

   **Ожидаемый результат.** Лампа горит.

2. **Вариант 2.** Выбрать второй сигнал.
   **Основание.** [R-D002-01](#r-d002-01) «Лампа мигает».

   **Ожидаемый результат.** Лампа мигает.'''
        verify_choices(options, body, 'fixture')
        for broken in (options.replace('R-D002-01', 'R-D003-01'),
                       options.replace('Лампа мигает.', 'Лампа горит.'),
                       options.replace('«Лампа горит»', '«Лампа погасла»'),
                       options.replace('**Основание.**', 'Примечание', 1)):
            with self.subTest(broken=broken), self.assertRaises(ValueError):
                verify_choices(broken, body, 'fixture')


class BlockingQuestionReadbackTests(unittest.TestCase):
    question = 'Какой сигнал увидит оператор?'
    open_premise = ('**Предполагаемый пробел · Полнота · Существенная.** Неясен режим.\n\n'
                    '**Что нужно уточнить.** Выбран ли дневной режим?\n\n'
                    '**Как ответ изменит приёмку.** Видимый сигнал зависит от режима.')
    direct_defect = ('**Дефект · Проверяемость · Существенная.** Описан обязательный сигнал.\n\n'
                     '[R-D002-01](#r-d002-01) · [строка 7](source.md#L7)\n\n> Лампа мигает.  \n\n'
                     '**Предложение для автора.** Предложение модели.\n\n'
                     f'**Вопрос для решения.** {question}\n\nУточнить сигнал.\n\n'
                     '**Черновик приёмочного теста.** Запустить сигнал.')

    def report(self, members, *bodies, scenario='Включить дневной режим.'):
        links = ', '.join(f'[Z-{i:03}](#z-{i:03})' for i in members)
        section = (f'## Вопросы к автору ТЗ\n\n**{self.question}**\n\n'
                   f'Блокирует приёмку · {links}. Зависимый сценарий — {scenario}\n\n<a id="findings"></a>')
        cards = [f'<a id="z-{i:03}"></a>\n\n### Z-{i:03} · {self.question}\n\n{body}'
                 for i, body in enumerate(bodies, 1)]
        return '\n\n'.join([section, *cards])

    def test_mixed_group_can_block_on_direct_card_with_same_question(self):
        report = self.report([2, 1], self.open_premise, self.direct_defect)
        self.assertEqual(verify_proposals(report, 'fixture', 2), 1)

    def test_single_open_card_cannot_borrow_a_defect_mentioned_in_scenario(self):
        report = self.report([1], self.open_premise, self.direct_defect,
                             scenario='См. также [Z-002](#z-002).')
        with self.assertRaisesRegex(ValueError, 'нет другого основания'):
            verify_proposals(report, 'fixture', 2)

    def test_group_of_two_open_cards_cannot_block(self):
        report = self.report([1, 2], self.open_premise, self.open_premise)
        with self.assertRaisesRegex(ValueError, 'нет другого основания'):
            verify_proposals(report, 'fixture', 2)

    def test_critical_open_card_is_invalid_even_in_supported_group(self):
        report = self.report([1, 2], self.open_premise.replace('Существенная', 'Критичная'), self.direct_defect)
        with self.assertRaisesRegex(ValueError, 'открытая предпосылка помечена критичной'):
            verify_proposals(report, 'fixture', 2)

    def test_mixed_group_requires_evidence_priority_and_the_same_question(self):
        for invalid in (self.direct_defect.replace(self.question, 'Кому доступна настройка?'),
                        self.direct_defect.replace('> Лампа мигает.', 'Лампа мигает.'),
                        self.direct_defect.replace('Существенная', 'Низкая'),
                        self.direct_defect.replace('**Дефект ·', '**Рекомендация ·'),
                        self.direct_defect.replace('**Вопрос для решения.**', 'Тема:')):
            with self.subTest(card=invalid), self.assertRaisesRegex(ValueError, 'нет другого основания'):
                verify_proposals(self.report([1, 2], self.open_premise, invalid), 'fixture', 2)

    def test_open_id_in_scenario_does_not_join_an_unrelated_blocking_group(self):
        report = self.report([2], self.open_premise, self.direct_defect, scenario='См. также [Z-001](#z-001).')
        self.assertEqual(verify_proposals(report, 'fixture', 2), 1)
