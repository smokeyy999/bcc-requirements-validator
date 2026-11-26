import unittest

from requirements_validator.engine import _adjudicate_one
from tests.test_engine import checked_question


class PremiseReviewTests(unittest.TestCase):
    def setUp(self):
        evidence = [{"id": "R-A-01", "quote": "Показание перед циклом сохраняется."},
                    {"id": "R-B-01", "quote": "За цикл счётчик увеличился на три. Экран показывает пять."}]
        self.item = dict(id="Z-001", kind="Дефект", category="Противоречивость", counted=True,
                         topic="Значение после цикла", ids=[a["id"] for a in evidence], evidence=evidence,
                         question="Почему экран показывает неверный итог?", test="Проверить итог цикла.",
                         fix="", blocking=True, interpretations=[], proposal_options=[{"anchor": e} for e in evidence])
        self.decision = dict(id="Z-001", action="уточнить", question_mode="заменить",
                             basis="Обоснованное ожидание", severity="Существенная", blocking=False,
                             supports=list(self.item["ids"]), question="Чему равно начальное показание?",
                             test="Сверить показание до и после одного цикла.",
                             reason="Пример сообщает приращение, исходное показание в нём отсутствует.",
                             question_check=checked_question("R-A-01", "Показание до цикла сохранено.",
                                 "Каково исходное показание?", "Пример проходит с исходным значением два.",
                                 "При исходном нуле пример расходится с правилом."),
                             case_check=dict(status="требует ответа", condition="Начальное показание счётчика.",
                                             effect="При исходном значении два пример согласован, при нулевом — расходится.",
                                             anchors=evidence))

    def test_missing_initial_state_becomes_conditional_question(self):
        finding = _adjudicate_one(self.decision, self.item)
        self.assertEqual(finding["kind"], "Предполагаемый пробел")
        self.assertEqual(finding["open_premise"]["condition"], self.decision["case_check"]["condition"])
        self.assertEqual(finding["consequence"], self.decision["case_check"]["effect"])
        self.assertEqual(finding["topic"], self.decision["question"])
        self.assertFalse(finding["counted"] or finding["blocking"] or finding["proposal_options"])

    def test_missing_premise_cannot_support_a_confirmed_or_critical_finding(self):
        for edits in (dict(action="оставить", supports=[]), dict(severity="Критичная"),
                      dict(blocking=True), dict(supports=["R-A-01"])):
            with self.subTest(edits=edits), self.assertRaises(ValueError):
                _adjudicate_one(dict(self.decision, **edits), self.item)

    def test_common_conditions_must_be_grounded_on_both_sides_of_conflict(self):
        decision = dict(self.decision, action="оставить", basis="Прямое обязательство", supports=[])
        for anchors in (self.item["evidence"][:1], [dict(self.item["evidence"][0], quote="счётчик равен нулю")],
                        [dict(self.item["evidence"][0], id="R-NEW-01")]):
            case = dict(decision["case_check"], status="подтверждено", anchors=anchors)
            with self.subTest(anchors=anchors), self.assertRaises(ValueError):
                _adjudicate_one(dict(decision, case_check=case), self.item)

    def test_recategorization_cannot_skip_premise_check_for_critical_defect_or_ambiguity(self):
        unchecked = dict(status="не применимо", condition="", effect="", anchors=[])
        for kind, severity in (("Дефект", "Критичная"), ("Неоднозначность", "Существенная")):
            item = dict(self.item, kind=kind, category="Ясность")
            decision = dict(self.decision, action="оставить", basis="Прямое обязательство",
                            severity=severity, supports=[], case_check=unchecked)
            with self.subTest(kind=kind), self.assertRaisesRegex(ValueError, "применимости"):
                _adjudicate_one(decision, item)
