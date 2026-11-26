"""Синтетическое ТЗ о бронировании залов и фиксированные ответы транспорта."""

import copy
import json
import unittest
from dataclasses import dataclass
from types import SimpleNamespace

from requirements_validator.engine import AUDIT, GLOBAL, LOCAL, OPERATION, PATCH, VALUE, review


def agreed_audit():
    """Фиксированный ответ независимого рецензента для ТЗ про бронирование."""
    return {
        "decisions": [{"id": "Z-001", "action": "оставить", "basis": "Прямое обязательство",
                       "severity": "Критичная", "reason": "Цена отмены за сутки имеет два исхода.",
                       "blocking": True, "supports": [], "question_mode": "сохранить", "question": "", "test": ""}],
        "assessment": "Правила отмены устанавливают разные суммы.",
        "readiness": "Проверка суммы при отмене требует решения владельца.",
        "priorities": [{"ids": ["Z-001"], "step": "Уточнить плату за отмену."}],
    }


@dataclass
class Block:
    id: str
    text: str
    source_id: str | None = None
    section: str = "Бронирование зала"
    location: str = "строка 1"


class Responses:
    def __init__(self, *answers, audits=None):
        self.answers = iter(answers)
        self.audits = iter([agreed_audit()] if audits is None else audits)
        self.calls = []

    def ask(self, prompt, schema):
        auditing = schema is AUDIT or (schema is PATCH and self.calls[-1][1] is AUDIT)
        self.calls.append((prompt, schema))
        return copy.deepcopy(next(self.audits if auditing else self.answers))


class TestReview(unittest.TestCase):
    def setUp(self):
        self.first = "Снять бронь за сутки можно бесплатно."
        self.second = "Зал вмещает 20 человек."
        self.third = "При отмене за сутки удержать плату."
        self.blocks = [Block("M01", f"З-1. {self.first} {self.second}", "З-1"),
                       Block("M02", self.third, location="строка 2"),
                       Block("M03", "Подпись администратора: ____", location="строка 3")]
        self.document = SimpleNamespace(blocks=self.blocks)
        self.local = {
            "claims": [
                {"block": block, "quote": quote, "summary": quote, "assessment": check,
                 "status": "проверяемо", "trace": "локально"}
                for block, quote, check in (
                    ("M01", self.second, "Проверить заявленную вместимость."),
                    ("M01", self.first, "Проверить сумму удержания."),
                    ("M02", self.third, "Проверить списание при отмене."),
                )
            ],
            "context": [{"block": "M03", "role": "шаблон"}],
        }
        self.issue = {
            "topic": "Плата за отмену", "kind": "Дефект", "category": "Противоречивость",
            "severity": "Критичная", "reason": "Невозможно выбрать сумму удержания.",
            "scenario": "Посетитель отменяет бронь ровно за сутки.",
            "consequence": "Тест отмены ожидает одновременно нулевое и ненулевое списание.",
            "evidence": [{"id": "R-M01-01", "quote": self.first},
                         {"id": "R-M02-01", "quote": self.third}],
            "interpretations": [], "question": "Удерживать плату за отмену за сутки?",
            "test": "Отмена за сутки до начала.", "blocking": True, "fix": "", "reference": "",
        }
        self.whole = {
            "findings": [self.issue], "resolved": [], "traces": [],
            "scope": {"operations": "R-M01-01 — правило об оплате, без стандартизованного интерфейса.",
                      "values": "R-M01-02 — фиксированная вместимость зала."},
            "assessment": "Правила отмены описывают разные списания.",
            "readiness": "Тест списания при отмене требует решения владельца.",
            "priorities": ["Согласовать плату при отмене за сутки."],
        }

    def test_cross_section_result_and_coverage(self):
        duplicate = copy.deepcopy(self.issue)
        duplicate["evidence"].reverse()
        self.whole["findings"].append(duplicate)
        provider = Responses(self.local, self.whole)
        result = review(self.document, provider)
        self.assertEqual(result["counts"], dict(requirements=3, defects=1, ambiguities=0,
                                                gaps=0, recommendations=0, questions=1))
        first, second, third = result["requirements"]
        self.assertEqual(first["source_id"], second["source_id"])
        self.assertEqual(first["source_id"], "З-1")
        self.assertIsNone(third["source_id"])
        self.assertEqual(first["findings"], third["findings"])
        self.assertEqual(first["findings"], ["Z-001"])
        self.assertEqual(second["status"], "Нарушений не выявлено")
        self.assertEqual(result["findings"][0]["evidence"][1]["location"], "строка 2")
        self.assertTrue(result["questions"][0]["blocking"])
        self.assertIn("отмене", result["set_review"]["readiness"].lower())
        self.assertNotIn("карта", json.dumps(result, ensure_ascii=False).lower())
        self.assertEqual([schema for _, schema in provider.calls], [LOCAL, GLOBAL, AUDIT])
        self.assertIn(self.blocks[-1].text, provider.calls[-1][0])

    def test_separate_standard_reference_for_requested_operation_effect(self):
        method = "Клиент вызывает стандартный HTTP HEAD /reserve."
        effect = "Операция по запросу клиента оформляет новую бронь."
        self.blocks[0].text = method
        self.blocks[1].text = effect
        self.local["claims"] = [
            dict(self.local["claims"][0], block=b.id, quote=b.text, summary=b.text, trace="локально")
            for b in self.blocks[:2]
        ]
        self.issue.update(topic="Семантика бронирования", reference="safe",
                          reason="Выбранная операция несовместима с намерением оформить бронь.",
                          evidence=[{"id": "R-M01-01", "quote": method}, {"id": "R-M02-01", "quote": effect}])
        self.whole["scope"]["values"] = "R-M02-01 — действие оформления."
        with self.assertRaisesRegex(ValueError, "Нет трассы"):
            review(self.document, Responses(self.local, self.whole, self.whole))
        self.whole["traces"] = [
            dict(aspect=OPERATION, subjects=["R-M01-01"], supports=["R-M02-01"],
                 reasoning="Клиент требует создания брони.", finding_topic=self.issue["topic"])]
        provider = Responses(self.local, self.whole)
        result = review(self.document, provider)
        ref = result["findings"][0]["reference"]
        self.assertEqual(ref["url"], "https://www.rfc-editor.org/rfc/rfc9110.html#section-9.2.1")
        self.assertEqual([ev["quote"] for ev in result["findings"][0]["evidence"]], [method, effect])
        self.assertIn(ref["rule"], provider.calls[-1][0])

    def test_only_applicable_protocol_can_supply_a_reference(self):
        self.issue["reference"] = "safe"
        with self.assertRaisesRegex(ValueError, "отсутствует в справочнике"):
            review(self.document, Responses(self.local, self.whole, self.whole))

    def test_value_trace_requires_actual_provider_or_a_linked_question(self):
        self.blocks[0].text = "Терминал показывает число гостей в зале."
        self.local["claims"] = [
            dict(self.local["claims"][0], block=b.id, quote=b.text, summary=b.text,
                 trace=VALUE if i == 0 else "локально")
            for i, b in enumerate(self.blocks[:2])
        ]
        self.issue.update(kind="Предполагаемый пробел", category="Трассируемость",
                          topic="Источник числа гостей", evidence=[{"id": "R-M01-01", "quote": ""}],
                          question="Откуда терминал узнаёт число гостей?", test="Сверка при входе гостя.")
        trace = dict(aspect=VALUE, subjects=["R-M01-01"], supports=[],
                     reasoning="Терминалу нужны сведения о посетителях.", finding_topic="")
        self.whole["traces"] = [trace]
        for wrong_topic in ("", "Другая тема"):
            trace["finding_topic"] = wrong_topic
            with self.subTest(wrong_topic=wrong_topic), self.assertRaisesRegex(ValueError, "/traces/0"):
                review(self.document, Responses(self.local, self.whole, self.whole))
        trace["finding_topic"] = self.issue["topic"]
        result = review(self.document, Responses(self.local, self.whole))
        self.assertEqual(result["counts"]["gaps"], 1)
        self.assertEqual(result["counts"]["defects"], 0)

    def test_empty_scope_requires_grounded_explanation_even_with_local_labels_empty(self):
        self.whole["scope"]["values"] = "Проверка не требуется."
        with self.assertRaisesRegex(ValueError, "/scope/values"):
            review(self.document, Responses(self.local, self.whole, self.whole))

    def test_missing_block_retried_alone_with_read_only_neighbours(self):
        bad = dict(self.local, context=[])
        repaired = {"claims": [], "context": self.local["context"]}
        provider = Responses(bad, repaired, self.whole)
        result = review(self.document, provider)
        self.assertEqual(len(provider.calls), 4)
        payload = json.loads(provider.calls[1][0].split("Вход (JSON):\n", 1)[1])
        self.assertEqual([b["id"] for b in payload["blocks"]], ["M03"])
        self.assertEqual([b["id"] for b in payload["context_only"]], ["M02"])
        self.assertEqual(len(result["context"]), 1)

    def test_one_invalid_claim_replaces_whole_block(self):
        broken = copy.deepcopy(self.local)
        broken["claims"][1]["quote"] = "Выдумка"
        broken["claims"][0]["summary"] = "Этот устаревший текст следует убрать."
        repaired = {"claims": self.local["claims"][:2], "context": []}
        provider = Responses(broken, repaired, self.whole)
        result = review(self.document, provider)
        payload = json.loads(provider.calls[1][0].split("Вход (JSON):\n", 1)[1])
        self.assertEqual([b["id"] for b in payload["blocks"]], ["M01"])
        self.assertIn("не найдена", payload["errors"]["M01"])
        self.assertEqual(len(result["requirements"]), 3)
        self.assertNotIn("устаревший", json.dumps(result, ensure_ascii=False))

    def test_retry_schema_errors_and_retains_valid_blocks(self):
        broken = copy.deepcopy(self.local)
        broken["claims"][2]["summary"] = None
        repaired = {"claims": self.local["claims"][2:], "context": []}
        provider = Responses(broken, repaired, self.whole)
        result = review(self.document, provider)
        payload = json.loads(provider.calls[1][0].split("Вход (JSON):\n", 1)[1])
        self.assertEqual([b["id"] for b in payload["blocks"]], ["M02"])
        self.assertEqual([b["id"] for b in payload["context_only"]], ["M01", "M03"])
        self.assertEqual(result["counts"]["requirements"], 3)

    def test_unaddressable_rows_never_enter_report(self):
        self.local["claims"].append(dict(self.local["claims"][0], block="unrelated"))
        progress = []
        result = review(self.document, Responses(self.local, self.whole), progress.append)
        self.assertTrue(any("Отклонены записи" in row for row in progress))
        self.assertEqual(result["counts"]["requirements"], 3)

    def test_empty_reference_expands_validated_quote(self):
        self.issue["evidence"][0]["quote"] = ""
        result = review(self.document, Responses(self.local, self.whole))
        self.assertEqual(result["findings"][0]["evidence"][0]["quote"], self.first)
        self.issue["evidence"][0]["id"] = "R-invalid"
        with self.assertRaisesRegex(ValueError, "Неизвестный ID"):
            review(self.document, Responses(self.local, self.whole, self.whole))

    def test_unaligned_or_nonexistent_anchor_rejected(self):
        for broken in ({"id": "R-M01-12", "quote": self.first},
                       {"id": "R-M01-01", "quote": self.second},
                       {"id": "R-M01-01", "quote": "Выдуманный текст."}):
            with self.subTest(broken=broken):
                bad = copy.deepcopy(self.whole)
                bad["findings"][0]["evidence"][0] = broken
                with self.assertRaisesRegex(ValueError, "Повторный ответ"):
                    review(self.document, Responses(self.local, bad, bad))

    def test_resolves_local_risk_using_context(self):
        self.local["claims"][0]["status"] = "недостаточно данных"
        with self.assertRaisesRegex(ValueError, "Нет результата"):
            review(self.document, Responses(self.local, self.whole, self.whole))
        self.whole["resolved"] = [{"id": "R-M01-02", "reason": "Вместимость прямо указана."}]
        claim = review(self.document, Responses(self.local, self.whole))["requirements"][1]
        self.assertEqual(claim["assessment"], "Вместимость прямо указана.")

    def test_global_correction_only_appends_missing_resolution(self):
        self.local["claims"][0]["status"] = "проверить"
        correction = {"changes": [{"op": "append", "path": "/resolved/-",
                                   "value": json.dumps({"id": "R-M01-02", "reason": "Указано число мест."})}]}
        log = []
        provider = Responses(self.local, self.whole, correction)
        result = review(self.document, provider, log.append)
        self.assertEqual([schema for _, schema in provider.calls], [LOCAL, GLOBAL, PATCH, AUDIT])
        self.assertTrue(any("Нет результата" in line and "R-M01-02" in line for line in log))
        self.assertEqual(result["requirements"][1]["assessment"], "Указано число мест.")
        self.assertEqual(result["counts"]["defects"], 1)

    def test_same_rule_can_have_resolved_and_independent_finding(self):
        self.whole["resolved"] = [{"id": "R-M01-01", "reason": "Срок отмены прямо указан."}]
        result = review(self.document, Responses(self.local, self.whole))
        claim = result["requirements"][0]
        self.assertEqual(claim["findings"], ["Z-001"])
        self.assertIn("Срок отмены прямо указан.", claim["assessment"])
        self.assertEqual(claim["status"], "Выявлено нарушение")

    def test_patch_cannot_overwrite_good_results(self):
        self.local["claims"][0]["status"] = "проверить"
        for path in ("/readiness", "/findings", "/findings/0/topic", "/resolved/../findings"):
            with self.subTest(path=path):
                patch = {"changes": [{"op": "replace", "path": path, "value": "Посторонняя замена"}]}
                with self.assertRaisesRegex(ValueError, "вне разрешённой области"):
                    review(self.document, Responses(self.local, self.whole, patch))

    def test_valid_patch_must_pass_complete_revalidation(self):
        self.local["claims"][0]["status"] = "проверить"
        patch = {"changes": [{"op": "append", "path": "/resolved/-",
                              "value": json.dumps({"id": "R-fake", "reason": "не подтверждено"})}]}
        with self.assertRaisesRegex(ValueError, "Проверьте|Повторный ответ"):
            review(self.document, Responses(self.local, self.whole, patch))

    def test_audit_can_replace_one_scalar_and_remove_two_original_duplicates(self):
        audit = agreed_audit()
        good = audit["decisions"][0]
        # Правка первого вердикта плюс удаление обоих дублей по исходным индексам.
        audit["decisions"] = [dict(good, reason=""), good, good]
        changes = {"changes": [
            {"op": "replace", "path": "/decisions/0/reason", "value": good["reason"]},
            {"op": "remove", "path": "/decisions/1", "value": ""},
            {"op": "remove", "path": "/decisions/2", "value": ""},
        ]}
        provider = Responses(self.local, self.whole, audits=[audit, changes])
        result = review(self.document, provider)
        self.assertEqual(result["counts"]["defects"], 1)
        self.assertIs(provider.calls[-1][1], PATCH)

    def test_two_supported_readings_are_counted(self):
        self.issue.update(kind="Неоднозначность", category="Однозначность",
                          interpretations=[dict(self.issue["evidence"][0],
                                                quote="", reading="Свободная отмена", effect="Удержание нулевое"),
                                           dict(self.issue["evidence"][1],
                                                reading="Платная отмена", effect="Есть списание")])
        result = review(self.document, Responses(self.local, self.whole))
        self.assertEqual((result["counts"]["defects"], result["counts"]["ambiguities"]), (1, 1))
        self.assertIn("R-M02-01", result["findings"][0]["interpretations"][1])
        self.assertIn(self.first, result["findings"][0]["interpretations"][0])
        self.issue["interpretations"][1]["effect"] = "Удержание нулевое"
        with self.assertRaisesRegex(ValueError, "различаться"):
            review(self.document, Responses(self.local, self.whole, self.whole))

    def test_gap_excluded_from_defect_count(self):
        self.issue.update(kind="Предполагаемый пробел", category="Полнота")
        result = review(self.document, Responses(self.local, self.whole))
        self.assertEqual(result["counts"]["defects"], 0)
        self.assertEqual(result["counts"]["gaps"], 1)
        self.assertEqual(result["requirements"][0]["status"], "Недостаточно данных")

    def test_retracted_candidate_leaves_no_issue_or_question(self):
        audit = agreed_audit()
        audit["decisions"][0].update(action="снять", basis="Вне требований", blocking=False,
                                     reason="Приведённый сценарий не входит в правила открытия зала.",
                                     question_mode="убрать")
        audit.update(assessment="Требования к открытию зала проверяемы.", readiness="Можно тестировать.",
                     priorities=[])
        result = review(self.document, Responses(self.local, self.whole, audits=[audit]))
        self.assertEqual(result["counts"]["defects"], 0)
        self.assertFalse(result["questions"])
        self.assertFalse(result["findings"])
        self.assertFalse(result["set_review"]["priorities"])
        self.assertEqual(result["requirements"][0]["assessment"], audit["decisions"][0]["reason"])
        self.assertEqual(result["requirements"][0]["status"], "Нарушений не выявлено")

    def test_question_downgrade_keeps_only_verified_source(self):
        audit = agreed_audit()
        audit["decisions"][0].update(action="уточнить", basis="Обоснованное ожидание", blocking=False,
                                     severity="Низкая", reason="Размер суммы упоминается для одного условия.",
                                     supports=["R-M02-01"], question_mode="заменить",
                                     question="К какому условию относится удержание?", test="Отмена зала за сутки.")
        result = review(self.document, Responses(self.local, self.whole, audits=[audit]))
        [f] = result["findings"]
        self.assertEqual(result["counts"]["defects"], 0)
        self.assertEqual(result["counts"]["gaps"], 1)
        self.assertEqual(f["ids"], ["R-M02-01"])
        self.assertEqual([a["quote"] for a in f["evidence"]], [self.third])
        self.assertFalse(f["interpretations"])
        self.assertEqual(result["questions"][0]["test"], "Отмена зала за сутки.")
        self.assertFalse(result["questions"][0]["blocking"])
        self.assertEqual(result["requirements"][0]["findings"], [])

    def test_audit_rejects_missing_duplicate_or_speculative_verdicts(self):
        baseline = agreed_audit()
        row = baseline["decisions"][0]
        for decisions in ([], [row, row], [dict(row, id="Z-002")],
                          [dict(row, basis="Обоснованное ожидание")],
                          [dict(row, action="уточнить", supports=["R-M01-02"])]):
            with self.subTest(decisions=decisions):
                bad = dict(baseline, decisions=decisions)
                with self.assertRaisesRegex(ValueError, "Повторный ответ"):
                    review(self.document, Responses(self.local, self.whole, audits=[bad, bad]))

    def test_withdrawn_id_rejected_in_final_priorities(self):
        audit = agreed_audit()
        audit["decisions"][0].update(action="снять", question_mode="убрать", blocking=False)
        with self.assertRaisesRegex(ValueError, "снятое"):
            review(self.document, Responses(self.local, self.whole, audits=[audit, audit]))

    def test_schema_and_invalid_quote_rejected(self):
        bad = copy.deepcopy(self.local)
        bad["claims"][0]["quote"] = "Другое требование"
        for answer in (None, {"claims": [], "contexts": []}, bad):
            with self.subTest(answer=answer):
                with self.assertRaisesRegex(ValueError, "Повторный ответ"):
                    review(self.document, Responses(answer, answer))

    def test_chunks_still_reach_one_complete_review(self):
        self.blocks[0].text += " " * 20100
        first = {"claims": self.local["claims"][:2], "context": []}
        second = {"claims": self.local["claims"][2:], "context": self.local["context"]}
        provider = Responses(first, second, self.whole)
        result = review(self.document, provider)
        self.assertEqual(result["counts"]["requirements"], 3)
        payload = json.loads(provider.calls[-1][0].split("Вход (JSON):\n", 1)[1])
        self.assertEqual(len(payload["blocks"]), 3)
        self.assertEqual(len(payload["claims"]), 3)
        self.assertEqual(len(provider.calls), 4)


if __name__ == "__main__":
    unittest.main()
