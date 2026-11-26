import unittest

from requirements_validator.refund_scope import refund_rules, refund_scope_error


class RefundScopeTests(unittest.TestCase):
    rule = "Возврат уменьшает расходы периода исходной покупки."
    amount = "Для каждого платежа хранится сумма покупки."
    partial = "Поддерживается ли частичный возврат и, если да, уменьшаются ли расходы на возвращённую сумму?"
    test = "Полный возврат 900 уменьшает расходы на 900. При поддержке частичного вернуть 300."
    good_outcomes = ["Частичный возврат 300 учтён, расходы уменьшены на 300.",
                     "Частичный возврат вне области функции; изменение итога по нему не принимается."]
    bad_outcomes = ["При полном возврате 900 расходы уменьшаются на 900.",
                    "При том же возврате расходы уменьшаются на иную величину."]

    def check(self, question, *, outcomes=None, source=(), checked=(), test=None):
        quotes = {"R1": self.rule, "R2": self.amount, **dict(source)}
        finding = dict(ids=["R1"], question=question, test=self.test if test is None else test,
                       question_basis=dict(checked_ids=["R1", "R2", *checked],
                                           outcomes=self.good_outcomes if outcomes is None else outcomes))
        return refund_scope_error(finding, {"question": question}, quotes)

    def test_full_and_partial_have_separate_decisions(self):
        generic = "Как вычисляется уменьшение расходов при полном возврате и, если поддерживается частичный возврат, при частичном?"
        self.assertTrue(self.check(generic, outcomes=self.bad_outcomes))
        self.assertTrue(self.check(self.partial, outcomes=self.bad_outcomes))
        self.assertFalse(self.check(self.partial))

    def test_only_an_exception_in_the_checked_refund_terms_changes_the_control(self):
        question = "На какую сумму уменьшаются расходы при полном возврате?"
        fee = ("fee", "При возврате удерживается комиссия по неизвестной ставке.")
        self.assertFalse(self.check(question, source=[fee], checked=["fee"]))
        self.assertTrue(self.check(question, source=[("fee", "За перевод взимается комиссия.")], checked=["fee"]))
        self.assertTrue(self.check(question, outcomes=self.bad_outcomes))

    def test_existing_scope_answer_is_not_requested_again(self):
        question = self.partial
        for quote in ("Частичные возвраты предусмотрены.", "Поддерживаются только полные возвраты.",
                      "Частичные возвраты не допускаются."):
            with self.subTest(quote=quote):
                self.assertIn("прямо задана", self.check(question, source=[("R3", quote)], checked=["R3"]))

    def test_timing_and_data_linkage_can_present_independent_questions(self):
        for question in ("К какому периоду относится частичный возврат?",
                         "Как связать частичный возврат с исходной покупкой?",
                         "К какому дню привязывать полный возврат суммы?"):
            with self.subTest(question=question):
                self.assertFalse(self.check(question))

    def test_rule_detector_needs_an_actual_reduction_of_spending(self):
        rows = [self.rule, "A refund reduces posted spending for the original period.",
                "Возврат не уменьшает расходы.", "A refund does not reduce expenses.",
                "Возврат книги уменьшает число экземпляров у читателя.",
                "Хранить сумму расходов и список возвратов."]
        claims = [dict(id=str(i), quote=row) for i, row in enumerate(rows)]
        self.assertEqual(refund_rules(claims), ["0", "1"])

    def test_a_question_only_needs_review_if_its_own_sources_include_the_rule(self):
        question = "Как вычисляется сумма при полном возврате?"
        finding = dict(ids=["other"], question=question, test=self.test, question_basis={})
        self.assertEqual(refund_scope_error(finding, finding, {"R1": self.rule, "other": "Сумма доставки."}), "")
        self.assertEqual(refund_scope_error(None, finding, {"R1": self.rule}), "")
