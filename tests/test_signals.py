import unittest
from types import SimpleNamespace

from requirements_validator.engine import DraftError, OPERATION, VALUE, _final_decisions, _set_result
from requirements_validator.signals import source_signals


def example(text, quotes=(), section="Профили измерений"):
    block = SimpleNamespace(id="M01", text=text, section=section)
    claims = [{"block": block.id, "id": f"R-M01-{i:02d}", "quote": quote, "status": "проверяемо"}
              for i, quote in enumerate(quotes, 1)]
    return block, claims


class SourceSignalTests(unittest.TestCase):
    def test_a_short_unit_should_not_link_an_unrelated_claim(self):
        rule = "Delay is measured in s"
        mapping = "2 means four minutes"
        b, claims = example("Status. " + rule + "; " + mapping + ".", ("Status", rule, mapping))
        signal, = source_signals([b], claims)
        self.assertEqual(signal["claims"], ["R-M01-02", "R-M01-03"])

    def test_declared_scale_and_interpretation_can_be_compared_without_model_arithmetic(self):
        rule = "Номинал задаётся в граммах"
        mapping = "значение 4 означает четыре килограмма"
        b, claims = example(rule + "; " + mapping + ".", (rule, mapping))
        signal, = source_signals([b], claims)
        self.assertEqual(signal["claims"], ["R-M01-01", "R-M01-02"])
        self.assertEqual((signal["by_declaration"], signal["by_example"], signal["base_unit"]),
                         ("4000", "4000000", "mg"))

    def test_equal_scales_separate_subjects_and_unrelated_dimensions_are_quiet(self):
        for text in ("Length is expressed in centimetres; 2.5 means 25 mm.",
                     "Масса задана в килограммах, значение 0,002 означает два грамма.",
                     "Интервал задан в минутах. Предел: значение 4 означает три секунды.",
                     "Высота задана в метрах; значение 11 означает девять секунд.",
                     "Температура позже уменьшится. Проверить показание после охлаждения."):
            with self.subTest(text=text):
                b, claims = example(text, (text,), section="Приёмочные испытания")
                self.assertEqual(source_signals([b], claims), [])

    def test_deferred_acceptance_may_be_grounded_elsewhere_but_cannot_be_silently_skipped(self):
        text = "Порядок испытания весов будет определён позднее."
        b, cs = example(text, (text,), section="План приёмки")
        signal, = source_signals([b], cs)
        self.assertEqual(signal["type"], "deferred_acceptance")
        raw = {"findings": [], "resolved": [], "traces": [], "priorities": [], "assessment": "Анализ.",
               "readiness": "Готово.", "scope": {"operations": cs[0]["id"], "values": cs[0]["id"]}}
        args = (raw, cs, {b.id: b}, {OPERATION: [], VALUE: []}, {}, [signal])
        with self.assertRaisesRegex(DraftError, "deferred_acceptance"):
            _set_result(*args)
        fact = dict(cs[0], id="R-M02-01", block="M02", quote="Откалибровать, приложить груз, сверить результат.")
        cs.append(fact)
        raw["resolved"] = [{"id": cs[0]["id"], "reason": "Полная проверка есть в приложении.",
                            "supports": [fact["id"]]}]
        self.assertIn(cs[0]["id"], _set_result(*args)[1])

    def test_numeric_example_is_not_evidence_for_its_own_override(self):
        raw = {"assessment": "Итог.", "readiness": "Готово.", "priorities": [], "findings": [],
               "traces": [], "scope": {"operations": "R-M01-01", "values": "R-M01-02"}}
        rule, mapping = "Пауза задана в минутах", "значение 2 означает четыре секунды"
        for prefix, allowed in (("", False), ("По умолчанию ", True)):
            b, cs = example(prefix + rule + "; " + mapping, (rule, mapping))
            signals = source_signals([b], cs)
            self.assertEqual(len(signals), 1)
            raw["resolved"] = [{"id": c["id"], "reason": "Частное толкование.", "supports": [cs[-1]["id"]]}
                               for c in cs]
            args = (raw, cs, {b.id: b}, {OPERATION: [], VALUE: []}, {}, signals)
            if allowed:
                self.assertEqual(len(_set_result(*args)[1]), 2)
            else:
                with self.assertRaisesRegex(DraftError, "unit_scale"):
                    _set_result(*args)

    def test_auditor_must_keep_the_pair_or_ground_its_withdrawal(self):
        a, b = "R-M01-01", "R-M01-02"
        cs = [{"id": a, "quote": "Интервал задан в секундах"}, {"id": b, "quote": "три минуты"}]
        candidate = {"id": "Z-001", "kind": "Неоднозначность", "category": "Однозначность", "counted": True,
                     "ids": [a, b], "evidence": [{"id": c["id"], "quote": c["quote"]} for c in cs]}
        case = {"status": "разные условия", "condition": "Заявлено особое толкование.", "effect": "",
                "anchors": list(candidate["evidence"])}
        decision = {"id": "Z-001", "action": "снять", "reason": "Использован особый формат.",
                    "question_mode": "убрать", "blocking": False, "question": "", "test": "",
                    "supports": [], "case_check": case, "severity": "Низкая",
                    "question_check": [], "same_decision_as": ""}
        audit = {"assessment": "Итог.", "readiness": "Готово.", "priorities": [], "decisions": [decision]}
        signal = {"type": "unit_scale", "block": "M01", "claims": [a, b], "qualified": False}
        with self.assertRaisesRegex(DraftError, "расхождение величин"):
            _final_decisions(audit, [candidate], cs, [signal])
        fact = {"id": "R-M03-01", "quote": "В другом профиле выбран независимый ввод."}
        cs.append(fact)
        case["anchors"].append(fact)
        self.assertEqual(_final_decisions(audit, [candidate], cs, [signal])[0], [])
