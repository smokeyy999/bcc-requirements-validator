import copy
import json
import unittest

from requirements_validator import engine as e
from tests import test_engine as fixtures


class TraceRepairTests(unittest.TestCase):
    def setUp(self):
        spec = fixtures.TestReview()
        spec.setUp()
        label = "Оператор видит сумму платы за отмену."
        spec.blocks[0].text = spec.blocks[0].text.replace(spec.second, label)
        spec.local["claims"][0].update(quote=label, summary=label, trace=e.VALUE)
        self.spec = spec
        self.subject = "R-M01-02"
        self.label = label
        spec.whole["traces"].append(dict(aspect=e.VALUE, subjects=[self.subject], supports=[],
                                         finding_topic=spec.issue["topic"], reasoning="Плата на экране зависит от правил отмены."))
        self.path = "/findings/0/evidence/-"
        self.anchor = {"id": self.subject, "quote": label}

    def change(self, path, value):
        return dict(op="append", path=path, value=json.dumps(value, ensure_ascii=False))

    def test_append_to_the_source_card_in_one_bounded_repair(self):
        spec = self.spec
        provider = fixtures.Responses(spec.local, spec.whole, {"changes": [self.change(self.path, self.anchor)]})
        repaired = e.review(spec.document, provider)
        self.assertEqual([s for _, s in provider.calls], [e.LOCAL, e.GLOBAL, e.PATCH, e.AUDIT])
        repair = json.loads(provider.calls[2][0].split("Вход (JSON):\n", 1)[1])
        self.assertIn(self.path, repair["allowed_paths"])
        self.assertNotIn("/findings/-", repair["allowed_paths"])
        self.assertIn(self.subject, repair["errors"])
        self.assertIn(spec.issue["topic"], repair["errors"])
        self.assertEqual(len(repaired["findings"]), 1)
        self.assertIn(self.subject, repaired["findings"][0]["ids"])
        spec.issue["evidence"].append(self.anchor)
        valid = fixtures.Responses(spec.local, spec.whole)
        self.assertEqual(e.review(spec.document, valid), repaired)
        self.assertEqual([s for _, s in valid.calls], [e.LOCAL, e.GLOBAL, e.AUDIT])

    def test_disallow_unrelated_evidence_invented_quotes_and_modification_of_valid_fields(self):
        spec = self.spec
        for label, changes, message in [
            ("известный, но лишний ID", [self.change(self.path, {"id":"R-M02-01", "quote":""})], "разрешены только"),
            ("несуществующий ID", [self.change(self.path, {"id":"R-X-01", "quote":""})], "разрешены только"),
            ("нет такой цитаты", [self.change(self.path, dict(self.anchor, quote="Не содержится в ТЗ."))], "Цитата не найдена"),
            ("изменение исходной темы", [dict(op="replace", path="/findings/0/topic", value="Изменённая тема")],
             "вне разрешённой"),
            ("дублирующая карточка", [self.change("/findings/-", spec.issue)], "вне разрешённой"),
        ]:
            with self.subTest(label=label), self.assertRaisesRegex(ValueError, message):
                e.review(spec.document, fixtures.Responses(spec.local, spec.whole, {"changes": changes}))

    def test_index_of_verified_card_preserves_its_position_after_an_invalid_predecessor(self):
        spec = self.spec
        invalid = copy.deepcopy(spec.issue)
        invalid["evidence"][0]["quote"] = "Отсутствующий фрагмент."
        spec.whole["findings"].insert(0, invalid)
        blocks = {b.id: b for b in spec.blocks}
        extracted = e._local_parts(spec.local, spec.blocks)[0]
        claims = [c for rows, _ in extracted.values() for c in rows]
        with self.assertRaises(e.DraftError) as raised:
            e._set_result(spec.whole, claims, blocks, {e.VALUE:[self.subject], e.OPERATION:[]}, {})
        self.assertIn("/findings/0", raised.exception.paths)
        self.assertEqual(raised.exception.evidence_ids, {"/findings/1/evidence/-": {self.subject}})

    def test_unavailable_ids_repeated_trace_and_missing_reason_report_distinct_repairs(self):
        spec = self.spec
        spec.issue["evidence"].append(self.anchor)
        valid = spec.whole["traces"][0]
        spec.whole["traces"].append(dict(valid, supports=["R-X-01"], reasoning=""))
        by_id = {key: {} for key in (self.subject, "R-M01-01", "R-M02-01")}
        findings = {0:dict(topic=spec.issue["topic"], ids=list(by_id))}
        errors, paths, _ = e._check_traces(spec.whole, by_id, {e.VALUE:[self.subject],e.OPERATION:[]}, findings)
        self.assertIn("/traces/1/supports/0", paths)
        self.assertIn("/traces/1/reasoning", paths)
        self.assertIn("/traces/1", paths)
        self.assertNotIn("/traces/0", paths)
        self.assertNotIn("/findings/-", paths)
        self.assertTrue(any("R-X-01" in error and "неизвестный" in error for error in errors))
        self.assertTrue(any(self.subject in error and "уже проверено" in error for error in errors))
