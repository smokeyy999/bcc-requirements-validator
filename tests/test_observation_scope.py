import unittest
from types import SimpleNamespace

from requirements_validator.observation_scope import measurement_scopes, scope_error


class ObservationScopeTests(unittest.TestCase):
    method = ("При закрытии люка загорается лампа и одновременно меняется цвет метки. "
              "Таймер измеряет целые секунды от закрытия люка до изменения цвета.")
    limit = "При приёмке время полного цикла по Т-1 не должно превышать пяти секунд, максимум 5 секунд."
    question = "С какой точностью при приёмке подтвердить совпадение изменения цвета и появления света?"

    def scopes(self, method=None, criterion=None, extra=()):
        inputs = [("Т-1", "Люк", method or self.method), ("Т-2", "Люк", criterion or self.limit), *extra]
        blocks = [SimpleNamespace(id=f"B{i}", source_id=rule, section=section, text=text)
                  for i, (rule, section, text) in enumerate(inputs)]
        claims = [dict(id=f"R{i}", block=b.id, quote=b.text) for i, b in enumerate(blocks)]
        return measurement_scopes(blocks, claims)

    def error(self, question, scopes, ids=("R0", "R1")):
        return scope_error(dict(question=question, ids=list(ids)), scopes)

    def test_additional_precision_for_unmeasured_stage(self):
        scopes = self.scopes()
        self.assertEqual(len(scopes), 1)
        self.assertTrue(scopes[0]["numeric_limit"])
        self.assertIn("промежуточных", self.error(self.question, scopes))
        self.assertEqual(self.error(self.question, scopes, ["different-stage"]), "")

    def test_missing_end_to_end_limit_remains_a_finding(self):
        scopes = self.scopes(criterion="При приёмке полный цикл по Т-1 должен быть достаточно быстрым.")
        self.assertFalse(scopes[0]["numeric_limit"])
        self.assertEqual(self.error("Какое наибольшее показание прибора проходит приёмку?", scopes), "")
        self.assertEqual(self.error("С какой точностью измерять длительность полного цикла?", scopes), "")

    def test_an_independent_stage_requirement_is_respected(self):
        for text in ("При приёмке отдельно измерить отставание метки от лампы.",
                     "Требуется согласовать точность синхронизации.",
                     "Задержка регистрации должна быть пренебрежимой.",
                     "Задержка регистрации не более 2 секунд."):
            with self.subTest(requirement=text):
                scopes = self.scopes(extra=[("К-1", "Контроль этапа", text)])
                self.assertEqual(scopes[0]["separate_test_ids"], ["R2"])
                self.assertEqual(self.error(self.question, scopes), "")

    def test_no_matching_boundaries_and_no_cross_operation_inference(self):
        self.assertEqual(self.scopes(method="Метка меняется одновременно с зажиганием лампы."), [])
        self.assertEqual(self.scopes(criterion="Для калибровки разрешены значения от нуля до пяти секунд."), [])
        scopes = self.scopes(extra=[("Д-1", "Люк", "Таймер измеряет от прихода письма до печати. "
                                    "При печати одновременно раздаются два звонка.")])
        self.assertEqual(scopes[0]["linked_event_ids"], ["R0"])
        self.assertEqual(self.error(self.question, scopes, ["R2"]), "")

    def test_real_other_decisions_are_kept(self):
        scopes = self.scopes()
        self.assertEqual(self.error("Какое конечное состояние должно получиться у замка?", scopes), "")
        self.assertEqual(self.error("Что означает совпадение двух идентификаторов?", scopes), "")
        self.assertEqual(scope_error(None, scopes), "")

    def test_english_timing_contract(self):
        scopes = self.scopes(
            method="At the same time a light comes on. A timer measures from closing the hatch to the light.",
            criterion="For acceptance the total time must be at most 5 seconds.")
        self.assertIn("промежуточных", self.error("What tolerance applies to simultaneous changes?", scopes))
