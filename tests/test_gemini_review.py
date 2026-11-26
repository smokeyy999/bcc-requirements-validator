import copy
import unittest
from types import SimpleNamespace

from requirements_validator import engine
from requirements_validator.gemini_review import FOCI, audit_review, cross_review
from tests.test_engine import Block
from tests import test_engine as examples


class GeminiGroundingTest(unittest.TestCase):
    def test_repairs_only_rejected_id_and_keeps_verified_decision(self):
        texts = ["Счётчик показывает число свободных кресел.", "Контроллер передаёт число свободных кресел."]
        block_list = [Block("M001", texts[0]), Block("M002", texts[1])]
        blocks = {b.id: b for b in block_list}
        claims = [dict(id=f"R-{b.id}-01", block=b.id, quote=b.text, summary=b.text, status="проверяемо") for b in block_list]
        ids = [c["id"] for c in claims]
        payload = {"blocks": [engine._source(b) for b in block_list], "claims": claims}
        head = dict(reviews={key: [] for key in FOCI}, extra_operations=[], extra_values=[],
                    scope={"operations": ids[1] + " — передача показания.", "values": ids[0] + " — показание."},
                    assessment="Набор описывает экран.", readiness="Можно реализовать.", priorities=[])
        good = {"reason": "Передача контроллера объясняет число.", "supports": [ids[1]], "finding_topic": ""}
        first = {"decisions": {"q0": good, "q1": dict(good, supports=["R-M777-01"])}, "new_findings": []}
        repair = {"decisions": {"q1": good}, "new_findings": []}
        calls = []
        def ask(prompt, schema):
            calls.append((prompt, schema))
            self.assertIn(texts[0], prompt)
            self.assertIn(texts[1], prompt)
            return copy.deepcopy([head, first, repair][len(calls)-1])
        candidates, resolved, trace = cross_review(SimpleNamespace(ask=ask), payload, claims, blocks,
                                                   {engine.OPERATION: [], engine.VALUE: ids}, {}, lambda _: None)
        self.assertEqual(candidates, [])
        self.assertEqual([t["subjects"] for t in trace["traces"]], [[ids[0]], [ids[1]]])
        self.assertEqual(calls[-1][1]["properties"]["decisions"]["required"], ["q1"])
        self.assertEqual(trace["traces"][0]["reasoning"], good["reason"])

    def test_audit_with_no_claims_or_candidates_fabricates_no_verdicts(self):
        summary = {"assessment": "Только шаблон.", "readiness": "Проверяемых правил нет.", "priorities": []}
        result = audit_review(SimpleNamespace(ask=lambda prompt, schema: summary), {"blocks": []}, [], [], lambda _: None)
        self.assertEqual(result, ([], {}, summary))

    def test_effective_question_is_applied_through_regular_adjudicator(self):
        fixture = examples.TestReview()
        fixture.setUp()
        blocks = {b.id: b for b in fixture.blocks}
        extracted = engine._local_parts(fixture.local, fixture.blocks)[0]
        claims = [c for rows, _ in extracted.values() for c in rows]
        one = engine._finding(fixture.issue, {c["id"]: c for c in claims}, blocks, {})
        candidates = engine._merge([one])
        decision = examples.agreed_audit()["decisions"][0]
        wire = {k: v for k, v in decision.items() if k not in ("id", "question_mode")}
        wire.update(question="Какую сумму удерживают?", test="Сверить итог отмены за сутки.",
                    case_scope="те же условия", scope_reason="В обеих строках бронь отменяют за сутки.")
        summary = {k: v for k, v in examples.agreed_audit().items() if k != "decisions"}
        answers = iter([{"Z-001": wire}, summary])
        findings, _, _ = audit_review(SimpleNamespace(ask=lambda *args: next(answers)), {}, candidates, claims, lambda _: None)
        self.assertEqual(findings[0]["question"], wire["question"])
        self.assertEqual(findings[0]["test"], wire["test"])
        self.assertTrue(findings[0]["counted"])
        wrong_scope = dict(wire, case_scope="частный случай", scope_reason="Субъекты требований различаются.")
        with self.assertRaisesRegex(ValueError, "одинаковых условиях"):
            audit_review(SimpleNamespace(ask=lambda *args: {"Z-001": wrong_scope}), {},
                         candidates, claims, lambda _: None)

    def test_duplicate_requires_identical_rule_evidence_and_topic_across_categories(self):
        fixture = examples.TestReview()
        fixture.setUp()
        blocks = {b.id: b for b in fixture.blocks}
        extracted = engine._local_parts(fixture.local, fixture.blocks)[0]
        claims = [c for rows, _ in extracted.values() for c in rows]
        base = engine._finding(fixture.issue, {c["id"]: c for c in claims}, blocks, {})
        a = dict(base, reference={"title": "Правило оформления", "url": "https://example.invalid/rule"})
        b = dict(a, category="Проверяемость", scenario="Другое описание той же отмены.")
        self.assertEqual(len(engine._merge([copy.deepcopy(a), copy.deepcopy(b)])), 2)
        self.assertEqual(len(engine._merge([copy.deepcopy(a), copy.deepcopy(b)], merge_review_directions=True)), 1)
        distinct = dict(b, topic="Другой вопрос по бронированию")
        self.assertEqual(len(engine._merge([copy.deepcopy(a), distinct], merge_review_directions=True)), 2)
