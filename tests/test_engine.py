"""Синтетическое ТЗ о бронировании залов и фиксированные ответы транспорта."""

import copy
import json
import unittest
from dataclasses import dataclass
from types import SimpleNamespace

from requirements_validator.engine import AUDIT, GLOBAL, LOCAL, OPERATION, PATCH, VALUE, _apply_patch, review
from requirements_validator.report import author_proposal


def checked_question(ident, known, decision, first, second, state="открытый выбор"):
    return [dict(state=state, obligation_id=ident, checked_ids=[ident], known_answer=known,
                 decision=decision, outcomes=[first, second])]


def agreed_audit():
    """Фиксированный ответ независимого рецензента для ТЗ про бронирование."""
    return {
        "decisions": [{"id": "Z-001", "action": "оставить", "basis": "Прямое обязательство",
                       "severity": "Критичная", "reason": "Цена отмены за сутки имеет два исхода.",
                       "blocking": True, "supports": [], "question_mode": "сохранить", "question": "", "test": "",
                       "question_check": [], "same_decision_as": "",
                       "case_check": {"status": "подтверждено", "condition": "Бронь отменяют за сутки.",
                                      "effect": "", "anchors": [{"id": "R-M01-01", "quote": "за сутки"},
                                                                  {"id": "R-M02-01", "quote": "за сутки"}]}}],
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
            "interpretations": [
                dict(id="R-M01-01", quote="", reading="Разрешить бесплатную отмену за сутки.", effect="Плата не списана."),
                dict(id="R-M02-01", quote="", reading="При отмене за сутки удержать плату.", effect="Плата списана."),
            ], "question": "Удерживать плату за отмену за сутки?",
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

    def test_matching_topic_anchors_and_scenario_retain_an_independent_outcome_for_review(self):
        duplicate = copy.deepcopy(self.issue)
        independent = copy.deepcopy(self.issue)
        independent.update(consequence="Нельзя определить доступность освободившегося зала.",
                           question="Когда зал снова доступен?", test="Проверить доступность после отмены.")
        duplicate["evidence"].append({"id": "R-M01-02", "quote": self.second})
        self.whole["findings"].extend([duplicate, independent])
        audit = agreed_audit()
        audit["decisions"].append(dict(audit["decisions"][0], id="Z-002"))
        result = review(self.document, Responses(self.local, self.whole, audits=[audit]))
        self.assertEqual(result["counts"]["questions"], 2)
        self.assertEqual(result["counts"]["defects"], 2)
        first = next(f for f in result["findings"] if f["question"] == self.issue["question"])
        self.assertEqual(set(first["ids"]), {"R-M01-01", "R-M01-02", "R-M02-01"})
        self.assertIn(independent["question"], [q["question"] for q in result["questions"]])

    def test_repair_rejected_applicability_object_or_only_its_array(self):
        valid_case = agreed_audit()["decisions"][0]["case_check"]
        for field, corrected in (("case_check", valid_case), ("case_check/anchors", valid_case["anchors"])):
            with self.subTest(field=field):
                audit = agreed_audit()
                audit["decisions"][0]["case_check"]["anchors"] = []
                patch = {"changes": [{"op": "replace", "path": f"/decisions/0/{field}",
                                      "value": json.dumps(corrected, ensure_ascii=False)}]}
                provider = Responses(self.local, self.whole, audits=[audit, patch])
                result = review(self.document, provider)
                self.assertEqual(result["counts"]["defects"], 1)
                self.assertEqual(result["findings"][0]["shared_premise"]["anchors"], valid_case["anchors"])
                self.assertEqual([schema for _, schema in provider.calls], [LOCAL, GLOBAL, AUDIT, PATCH])
                self.assertIn("/decisions/0/case_check/anchors (Z-001)", provider.calls[-1][0])

    def test_nested_repair_keeps_valid_neighbour_and_collection_protected(self):
        audit = agreed_audit()
        audit["decisions"].append(dict(copy.deepcopy(audit["decisions"][0]), id="Z-002"))
        before = copy.deepcopy(audit)
        for path, value in (("/decisions/1/case_check/anchors", []), ("/decisions", []),
                            ("/priorities", [])):
            with self.subTest(path=path):
                patch = {"changes": [{"op": "replace", "path": path, "value": json.dumps(value)}]}
                with self.assertRaisesRegex(ValueError, path):
                    _apply_patch(audit, AUDIT, patch, ["/decisions/0", "/priorities"])
                self.assertEqual(audit, before)

    def test_nested_repair_requires_schema_and_original_evidence(self):
        path = "/decisions/0/case_check/anchors"
        for value, message in (({}, "требуется array"), ([{"id": "R-M01-01", "quote": "выдумано"}], "дословные")):
            with self.subTest(value=value):
                audit = agreed_audit()
                audit["decisions"][0]["case_check"]["anchors"] = []
                patch = {"changes": [{"op": "replace", "path": path, "value": json.dumps(value)}]}
                with self.assertRaisesRegex(ValueError, message):
                    review(self.document, Responses(self.local, self.whole, audits=[audit, patch]))

    def test_nested_repair_limits_changes_in_aggregate(self):
        path = "/decisions/0/case_check/anchors"
        audit = agreed_audit()
        replacement = audit["decisions"][0]["case_check"]["anchors"] * 100
        patch = {"changes": [{"op": "replace", "path": path, "value": json.dumps(replacement)}]}
        with self.assertRaisesRegex(ValueError, "лимит"):
            _apply_patch(audit, AUDIT, patch, ["/decisions/0"])

    def test_nested_replacement_cannot_silently_discard_an_edit_to_the_same_field(self):
        path = "/decisions/0/case_check/anchors"
        audit = agreed_audit()
        replace = {"op": "replace", "path": path, "value": "[]"}
        remove = {"op": "remove", "path": path + "/0", "value": ""}
        for operations in ([replace, remove], [remove, replace]):
            with self.subTest(operations=operations), self.assertRaisesRegex(ValueError, "пересекается"):
                _apply_patch(audit, AUDIT, {"changes": operations}, ["/decisions/0"])

    def test_contradiction_proposes_two_cited_choices_with_separate_acceptance_outcomes(self):
        result = review(self.document, Responses(self.local, self.whole))
        [finding] = result["findings"]
        proposal = "\n".join(author_proposal(finding))
        self.assertIn(self.issue["question"], proposal)
        for number, option in enumerate(self.issue["interpretations"], 1):
            chosen = proposal.split(f"{number}. **Вариант {number}.** ", 1)[1].split("\n2. **Вариант", 1)[0]
            self.assertIn(option["reading"], chosen)
            self.assertIn("**Ожидаемый результат.** " + option["effect"], chosen)
            self.assertIn("**Основание.** [" + option["id"] + "]", chosen)
            other = self.issue["interpretations"][2-number]["id"]
            self.assertIn("привести в соответствие [" + other + "]", chosen)
        self.assertNotIn("[условиях данного сценария]", proposal)

    def test_decision_rejects_an_unfounded_number_or_the_same_rule_on_both_sides(self):
        for field, value in (("reading", "При отмене удержать 37 процентов."),
                             ("id", self.issue["interpretations"][0]["id"])):
            answer = copy.deepcopy(self.whole)
            answer["findings"][0]["interpretations"][1][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "числовая константа|разные ID"):
                review(self.document, Responses(self.local, answer, answer))

    def test_internal_conflict_needs_choices_even_when_the_prose_describes_a_repair(self):
        self.issue.update(interpretations=[], fix="Отменить плату.")
        with self.assertRaisesRegex(ValueError, "два варианта решения"):
            review(self.document, Responses(self.local, self.whole, self.whole))

    def test_separate_standard_reference_for_requested_operation_effect(self):
        method = "Клиент вызывает стандартный HTTP HEAD /reserve."
        effect = "Операция по запросу клиента оформляет новую бронь."
        self.blocks[0].text = method
        self.blocks[1].text = effect
        self.local["claims"] = [
            dict(self.local["claims"][0], block=b.id, quote=b.text, summary=b.text, trace="локально")
            for b in self.blocks[:2]
        ]
        self.issue.update(topic="Семантика бронирования", reference="safe", interpretations=[],
                          reason="Выбранная операция несовместима с намерением оформить бронь.",
                          evidence=[{"id": "R-M01-01", "quote": method}, {"id": "R-M02-01", "quote": effect}])
        self.whole["scope"]["values"] = "R-M02-01 — действие оформления."
        with self.assertRaisesRegex(ValueError, "Нет трассы"):
            review(self.document, Responses(self.local, self.whole, self.whole))
        self.whole["traces"] = [
            dict(aspect=OPERATION, subjects=["R-M01-01"], supports=["R-M02-01"],
                 reasoning="Клиент требует создания брони.", finding_topic=self.issue["topic"])]
        audit = agreed_audit()
        audit["decisions"][0]["case_check"].update(condition="Вызов HEAD оформляет бронь.",
                                                    anchors=self.issue["evidence"])
        provider = Responses(self.local, self.whole, audits=[audit])
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
        self.issue.update(kind="Предполагаемый пробел", category="Трассируемость", interpretations=[],
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
        audit = agreed_audit()
        audit["decisions"][0]["question_check"] = checked_question(
            "R-M01-01", "Обещан счётчик гостей.", "Когда учитывается вошедший?",
            "Показание меняется при входе.", "Показание меняется после регистрации.")
        audit["decisions"][0]["case_check"] = {"status": "не применимо", "condition": "", "effect": "", "anchors": []}
        result = review(self.document, Responses(self.local, self.whole, audits=[audit]))
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
        self.whole["resolved"] = [{"id": "R-M01-02", "reason": "Вместимость прямо указана.", "supports": ["R-M01-02"]}]
        claim = review(self.document, Responses(self.local, self.whole))["requirements"][1]
        self.assertEqual(claim["assessment"], "Вместимость прямо указана.")
        self.assertEqual(claim["resolution_sources"], ["R-M01-02"])

    def test_global_correction_only_appends_missing_resolution(self):
        self.local["claims"][0]["status"] = "проверить"
        correction = {"changes": [{"op": "append", "path": "/resolved/-",
                                   "value": json.dumps({"id": "R-M01-02", "reason": "Указано число мест.",
                                                        "supports": ["R-M01-02"]})}]}
        log = []
        provider = Responses(self.local, self.whole, correction)
        result = review(self.document, provider, log.append)
        self.assertEqual([schema for _, schema in provider.calls], [LOCAL, GLOBAL, PATCH, AUDIT])
        self.assertTrue(any("Нет результата" in line and "R-M01-02" in line for line in log))
        self.assertEqual(result["requirements"][1]["assessment"], "Указано число мест.")
        self.assertEqual(result["counts"]["defects"], 1)

    def test_a_local_candidate_cannot_be_resolved_using_missing_or_unknown_sources(self):
        self.local["claims"][0]["status"] = "проверить"
        for supports in ([], ["R-ABSENT"]):
            with self.subTest(supports=supports):
                self.whole["resolved"] = [{"id": "R-M01-02", "reason": "Якобы разрешено исключением.",
                                           "supports": supports}]
                with self.assertRaisesRegex(ValueError, "/resolved/0/supports"):
                    review(self.document, Responses(self.local, self.whole, {"changes": []}))

    def test_same_rule_can_have_resolved_and_independent_finding(self):
        self.whole["resolved"] = [{"id": "R-M01-01", "reason": "Срок отмены прямо указан.", "supports": ["R-M01-01"]}]
        result = review(self.document, Responses(self.local, self.whole))
        claim = result["requirements"][0]
        self.assertEqual(claim["findings"], ["Z-001"])
        self.assertIn("Срок отмены прямо указан.", claim["assessment"])
        self.assertIn(result['findings'][0]['reason'], claim['assessment'])
        self.assertEqual(claim["status"], "Связано с нарушением в спецификации")

    def test_context_citation_does_not_invalidate_its_rule_or_publish_a_local_guess(self):
        self.issue["evidence"].append({"id": "R-M01-02", "quote": self.second})
        self.local["claims"][0]["assessment"] = "Нужно изменить вместимость зала."
        result = review(self.document, Responses(self.local, self.whole))
        context = result["requirements"][1]
        self.assertEqual(context["status"], "Связано с нарушением в спецификации")
        self.assertEqual(context["findings"], ["Z-001"])
        self.assertEqual(context["assessment"], result["findings"][0]["reason"])
        self.assertEqual(result["counts"]["defects"], 1)

    def test_downgraded_card_cannot_erase_or_duplicate_an_independent_finding(self):
        self.whole["findings"].append(dict(
            self.issue, topic="Условия по вместимости", kind="Предполагаемый пробел", category="Полнота",
            severity="Низкая", interpretations=[], blocking=False,
            evidence=[{"id": "R-M01-02", "quote": self.second}, {"id": "R-M01-01", "quote": self.first}]))
        audit = agreed_audit()
        audit["decisions"].append(dict(
            audit["decisions"][0], id="Z-002", action="уточнить", basis="Обоснованное ожидание",
            severity="Низкая", reason="Указана вместимость, условия рассадки открыты.", blocking=False,
            supports=["R-M01-02"], question_mode="заменить", question="Как расставляются места?",
            test="Проверить рассадку по выбранной схеме.",
            question_check=checked_question("R-M01-02", "Указана вместимость зала.", "Какая рассадка применяется?",
                                            "Места занимают рядами.", "Места занимают за столами."),
            case_check=dict(status="требует ответа", condition="Какая схема рассадки применима?",
                            effect="При разных схемах число доступных мест может различаться.",
                            anchors=[{"id": "R-M01-02", "quote": self.second}])))
        self.whole["resolved"] = [{"id": "R-M01-01", "reason": audit["decisions"][0]["reason"],
                                   "supports": ["R-M01-01", "R-M02-01"]}]
        first, capacity, _ = review(self.document, Responses(self.local, self.whole, audits=[audit]))["requirements"]
        self.assertEqual(first["findings"], ["Z-001"])
        self.assertEqual(first["assessment"], audit["decisions"][0]["reason"])
        self.assertEqual(capacity["findings"], ["Z-002"])
        self.assertEqual(capacity["assessment"], audit["decisions"][1]["reason"])

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
                              "value": json.dumps({"id": "R-fake", "reason": "не подтверждено", "supports": []})}]}
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
        self.issue.update(kind="Предполагаемый пробел", category="Полнота", interpretations=[])
        audit = agreed_audit()
        audit["decisions"][0]["question_check"] = checked_question(
            "R-M01-01", self.first, "Какая плата при отмене за сутки?", "Плата удержана.", "Плата не удержана.")
        result = review(self.document, Responses(self.local, self.whole, audits=[audit]))
        self.assertEqual(result["counts"]["defects"], 0)
        self.assertEqual(result["counts"]["gaps"], 1)
        self.assertEqual(result["requirements"][0]["status"], "Связано с вопросом к автору")

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

    def test_retraction_can_use_an_explicit_exception_from_another_source_passage(self):
        exception = "Плату удерживают только при отмене аренды всей площадки."
        self.blocks[2].text = exception
        self.local["context"] = []
        self.local["claims"].append(dict(self.local["claims"][0], block="M03", quote=exception,
                                         summary=exception, assessment="Проверить условия аренды."))
        audit = agreed_audit()
        decision = audit["decisions"][0]
        decision.update(action="снять", blocking=False, question_mode="убрать",
                        reason="Область платной отмены прямо ограничена типом аренды.")
        decision["case_check"].update(status="разные условия", condition="Бронирование зала и аренда всей площадки.")
        third = {"id": "R-M03-01", "quote": exception}
        decision["case_check"]["anchors"].append(third)
        audit.update(priorities=[], assessment="Правила разделены.", readiness="Можно проверять оба случая.")
        result = review(self.document, Responses(self.local, self.whole, audits=[audit]))
        self.assertFalse(result["findings"])
        self.assertIn(third["id"], result["requirements"][0]["resolution_sources"])
        third["quote"] = "Применяется более позднее из правил."
        with self.assertRaisesRegex(ValueError, "дословные"):
            review(self.document, Responses(self.local, self.whole, audits=[audit, {"changes": []}]))

    def test_context_cannot_replace_either_rule_of_a_dismissed_conflict(self):
        self.issue["evidence"].append({"id": "R-M01-02", "quote": self.second})
        audit = agreed_audit()
        audit.update(priorities=[])
        decision = audit["decisions"][0]
        decision.update(action="снять", blocking=False, question_mode="убрать")
        decision["case_check"].update(status="разные условия")
        decision["case_check"]["anchors"][1] = {"id": "R-M01-02", "quote": self.second}
        with self.assertRaisesRegex(ValueError, "обеих сторон"):
            review(self.document, Responses(self.local, self.whole, audits=[audit, {"changes": []}]))

    def test_question_downgrade_keeps_only_verified_source(self):
        audit = agreed_audit()
        audit["decisions"][0].update(action="уточнить", basis="Обоснованное ожидание", blocking=False,
                                     severity="Низкая", reason="Размер суммы упоминается для одного условия.",
                                     supports=["R-M02-01"], question_mode="заменить",
                                     question_check=checked_question(
                                         "R-M02-01", self.third, "Когда применяют удержание?",
                                         "Сумму перечислили залу.", "Плата осталась у посетителя."),
                                     question="К какому условию относится удержание?", test="Отмена зала за сутки.")
        audit["decisions"][0]["case_check"].update(
            status="требует ответа", condition="При каких условиях возникает плата?",
            anchors=[{"id": "R-M02-01", "quote": "удержать плату"}],
            effect="Если условие выполнено, проверяют удержание. Иначе надо определить исход отмены.")
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
