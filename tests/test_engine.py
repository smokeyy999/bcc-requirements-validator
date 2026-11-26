"""Синтетическое ТЗ о бронировании залов и фиксированные ответы транспорта."""

import copy
import json
import unittest
from dataclasses import dataclass
from types import SimpleNamespace

from requirements_validator.engine import GLOBAL, LOCAL, review


@dataclass
class Block:
    id: str
    text: str
    source_id: str | None = None
    section: str = "Бронирование зала"
    location: str = "строка 1"


class Responses:
    def __init__(self, *answers):
        self.answers = iter(answers)
        self.calls = []

    def ask(self, prompt, schema):
        self.calls.append((prompt, schema))
        return copy.deepcopy(next(self.answers))


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
                 "status": "проверяемо"}
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
            "test": "Отмена за сутки до начала.", "blocking": True, "fix": "",
        }
        self.whole = {
            "findings": [self.issue], "resolved": [],
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
        self.assertEqual([schema for _, schema in provider.calls], [LOCAL, GLOBAL])
        self.assertIn(self.blocks[-1].text, provider.calls[-1][0])

    def test_missing_block_retried_alone_with_read_only_neighbours(self):
        bad = dict(self.local, context=[])
        repaired = {"claims": [], "context": self.local["context"]}
        provider = Responses(bad, repaired, self.whole)
        result = review(self.document, provider)
        self.assertEqual(len(provider.calls), 3)
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
        self.assertEqual(len(provider.calls), 3)


if __name__ == "__main__":
    unittest.main()
