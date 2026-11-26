import unittest

from requirements_validator.command_rules import missing_conflict, scheduled_command_pairs
from requirements_validator.engine import DraftError, OPERATION, VALUE, _final_decisions, _set_result


BAN = "При заморозке все автоматические команды публикации афиши блокируются."
TIMER = "В режиме заморозки команда публикации афиши от таймера немедленно публикует афишу."


def claims(*quotes):
    return [dict(id=f"R-C{i}-01", block=f"C{i}", quote=q, status="проверяемо") for i, q in enumerate(quotes, 1)]


class CommandRuleTests(unittest.TestCase):
    def test_same_mode_operation_and_machine_trigger_have_two_source_anchors(self):
        rows = claims(BAN, TIMER)
        pair, = scheduled_command_pairs(rows + [dict(rows[1], id="R-C2-02")])
        self.assertEqual(pair["prohibition_ids"], ["R-C1-01"])
        self.assertEqual(pair["instance_ids"], ["R-C2-01", "R-C2-02"])
        self.assertEqual(pair["trigger"], "от таймера")
        ordinary = "В режиме заморозки планировщик выполняет команду публикации афиши."
        self.assertEqual(len(scheduled_command_pairs(claims(BAN, ordinary))), 1)
        booking = claims("При паузе любые автоматические команды бронирования мест игнорируются.",
                         "Во время паузы команда бронирования мест по расписанию бронирует места.")
        self.assertEqual(len(scheduled_command_pairs(booking)), 1)

    def test_different_operation_object_state_or_outcome_do_not_prove_a_conflict(self):
        variants = [
            TIMER.replace("заморозки", "подготовки"),
            TIMER.replace("публикации", "сохранения"),
            TIMER.replace("публикации афиши", "публикации каталога"),
            TIMER.replace("от таймера", "от оператора"),
            TIMER.replace("немедленно публикует", "не публикует"),
            TIMER.replace("немедленно публикует афишу", "попадает в журнал"),
            TIMER.replace("немедленно", "после выхода из заморозки"),
            TIMER.replace("немедленно", "только после подтверждения оператора"),
        ]
        for variant in variants:
            with self.subTest(variant=variant):
                self.assertFalse(scheduled_command_pairs(claims(BAN, variant)))
        self.assertFalse(scheduled_command_pairs(claims(BAN.replace("все", "некоторые"), TIMER)))
        self.assertFalse(scheduled_command_pairs(claims(BAN.replace("блокируются", "блокируются при сбое"), TIMER)))

    def test_exceptions_have_to_name_the_same_command_and_where_given_the_same_mode(self):
        qualification = "При заморозке запрет не распространяется на команды публикации афиши по таймеру."
        self.assertFalse(scheduled_command_pairs(claims(BAN, TIMER, qualification)))
        manual = "Команда публикации афиши от таймера требует подтверждения оператора."
        self.assertFalse(scheduled_command_pairs(claims(BAN, TIMER, manual)))
        for other in (qualification.replace("афиши", "каталога"), qualification.replace("заморозке", "проверке"),
                      qualification.replace("по таймеру", "по расписанию"),
                      manual.replace("требует", "не требует")):
            with self.subTest(other=other):
                self.assertEqual(len(scheduled_command_pairs(claims(BAN, TIMER, other))), 1)

    def test_synthesis_and_adjudication_reject_an_unwritten_trigger_exception(self):
        rows = claims(BAN, TIMER)
        pair, = scheduled_command_pairs(rows)
        ids = [r["id"] for r in rows]
        assertions = dict(findings=[], assessment="Проверено.", readiness="Проверено.", priorities=[], traces=[],
                          scope={"operations": ids[0], "values": ids[1]}, resolved=[
                              dict(id=r["id"], reason="У таймера может быть исключение.", supports=ids) for r in rows])
        with self.assertRaisesRegex(DraftError, "команды"):
            _set_result(assertions, rows, {}, {OPERATION: [], VALUE: []}, {}, scheduled=[pair])
        ev = [dict(id=r["id"], quote=r["quote"]) for r in rows]
        candidate = dict(id="Z-001", kind="Дефект", category="Противоречивость", counted=True,
                         ids=ids, evidence=ev, proposal_options=[dict(anchor=a) for a in ev])
        self.assertFalse(missing_conflict(pair, [candidate]))
        self.assertTrue(missing_conflict(pair, [dict(candidate, category="Полнота", kind="Предполагаемый пробел")]))
        decision = dict(id="Z-001", action="снять", reason="Предполагается исключение.", question_mode="убрать",
                        blocking=False, question="", test="", supports=[], severity="Низкая", question_check=[],
                        same_decision_as="", case_check=dict(status="разные условия",
                            condition="Неизвестно, покрывается ли таймер.", effect="", anchors=ev))
        result = dict(assessment="Проверено.", readiness="Проверено.", priorities=[], decisions=[decision])
        with self.assertRaisesRegex(DraftError, "команды"):
            _final_decisions(result, [candidate], rows, scheduled=[pair])
