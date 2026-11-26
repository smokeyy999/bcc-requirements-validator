import unittest

from requirements_validator.engine import _check_question
from requirements_validator.transition_result import missing_transition_result, named_transition_targets
from tests.test_engine import checked_question


class TransitionResultTests(unittest.TestCase):
    def setUp(self):
        self.ident = "R-A-01"
        self.rule = "При получении нечитаемого оттиска оформитель обязан присвоить ему указанную здесь архивную метку."
        self.quotes = {self.ident: self.rule}
        self.card = dict(kind="Дефект", category="Ясность", ids=[self.ident],
                         question="По какому признаку считать оттиск нечитаемым и какую метку ему присвоить?",
                         test="Подать уже признанный нечитаемым оттиск и сверить итоговую метку.")
        self.check, = checked_question(self.ident, self.rule, "Выбрать итоговую метку уже классифицированного оттиска.",
            "При признанном нечитаемым оттиске итоговая метка «Альфа».",
            "При том же оттиске итоговая метка «Бета».", state="не определено значение термина")

    def test_category_is_based_on_the_two_results_for_the_fixed_case(self):
        _check_question({"question_check": [self.check]}, self.card, self.quotes)
        self.assertEqual(self.card["category"], "Полнота")
        self.assertEqual(self.card["question_basis"]["state"], "не задан результат действия")
        self.assertEqual(self.card["question_basis"]["outcomes"], self.check["outcomes"])

    def test_two_independent_questions_keep_their_own_dimension(self):
        a = dict(self.card, kind="Предполагаемый пробел", question="Какой оттиск считать нечитаемым?")
        b = dict(self.card, question="Какую метку присвоить заведомо нечитаемому оттиску?")
        definition = dict(self.check, decision="Определить признак нечитаемого оттиска.",
                          outcomes=["Этот оттиск входит в условие обработки.", "Этот оттиск выходит из условия."])
        _check_question({"question_check": [definition]}, a, self.quotes)
        _check_question({"question_check": [self.check]}, b, self.quotes)
        self.assertEqual((a["category"], b["category"]), ("Ясность", "Полнота"))

    def test_address_timing_alternative_inputs_and_known_target_do_not_qualify(self):
        variations = [
            (self.rule, dict(decision="В каком разделе указан код метки?"), {}),
            (self.rule, dict(decision="Установить допустимое время до присвоения итоговой метки."), {}),
            (self.rule, dict(outcomes=["Если условие выполнено, метка А.", "Если условие не выполнено, метка Б."]), {}),
            (self.rule, dict(outcomes=["При признанном оттиске метка А.", "При том же оттиске метка А."]), {}),
            (self.rule, dict(outcomes=["При признанном оттиске тест проходит.", "При том же оттиске тест провален."]), {}),
            (self.rule.replace("метку.", "метку из таблицы S-93."), {}, {}),
            (self.rule, {}, {"R-B-01": "Архивная метка — «Альфа»."}),
            (self.rule.replace("указанную здесь архивную метку", "метку, которую выбрал оператор"), {}, {}),
        ]
        for rule, changes, other in variations:
            with self.subTest(rule=rule, changes=changes, other=other):
                self.assertFalse(missing_transition_result(self.card, dict(self.check, **changes),
                                                           {self.ident: rule, **other}))

    def test_evidence_belongs_to_the_action_and_not_a_neighbour_or_a_broken_reference(self):
        self.assertFalse(missing_transition_result(dict(self.card, ids=["R-B-01"]), self.check, self.quotes))
        self.assertFalse(missing_transition_result(dict(self.card, category="Трассируемость", missing_target="S-7"),
                                                   self.check, self.quotes))

    def test_result_predicate_with_a_common_subject_and_known_input(self):
        rule = "После сигнала об отказе блок обязан перевести привод в указанное здесь конечное положение."
        q = dict(self.check, decision="Какое конечное положение привода нужно при уже установленном отказе?",
                 outcomes=["После защитного перехода привод поднят.", "После защитного перехода привод опущен."])
        self.assertTrue(missing_transition_result(self.card, q, {self.ident: rule}))
        for outcomes in (["При первом входе привод поднят.", "При другом входе привод опущен."],
                         ["После перехода индикатор светлый.", "После перехода индикатор тёмный."],
                         ["После перехода тест успешен.", "После перехода тест провален."]):
            self.assertFalse(missing_transition_result(self.card, dict(q, outcomes=outcomes), {self.ident: rule}))

    def test_source_hint_is_scoped_to_a_mandatory_transition(self):
        samples = [self.rule, self.rule.replace("обязан", "может"),
                   self.rule.replace("метку.", "метку из таблицы S-93.")]
        self.assertEqual(named_transition_targets([dict(id=str(n),quote=quote) for n,quote in enumerate(samples)]), ["0"])

    def test_english_fixed_input_changes_only_the_prescribed_output(self):
        requirement = "For a damaged copy the printer must display the specified final code."
        card = dict(self.card, question="Which copies are damaged and what code must be shown?",
                    test="Submit one already classified copy.")
        proof = dict(self.check, decision="Choose the final code for a known damaged copy.",
                     outcomes=["For a known damaged copy the code is A.", "For the same copy the code is B."])
        self.assertTrue(missing_transition_result(card, proof, {self.ident: requirement}))
