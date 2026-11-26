"""Проверка внешнего основания на коротком синтетическом примере."""
import unittest
from pathlib import Path

from requirements_validator.report import author_proposal, render
from requirements_validator.source import read_document


class ReferenceRenderingTest(unittest.TestCase):
    def test_each_proposed_choice_retains_its_own_verified_clause(self):
        a = {'id': 'R-M0001-01', 'quote': 'При окончании смены дверь закрывается.'}
        b = {'id': 'R-M0003-01', 'quote': 'При окончании смены дверь остаётся открытой.'}
        f = dict(counted=True, evidence=[a, b], ids=[a['id'], b['id']], proposal_anchors=[a, b],
                 fix='Закрыть через шесть часов.', scenario='Окончание смены.', test='Проверить положение двери.')
        result = '\n'.join(author_proposal(f))
        for anchor in (a,b):
            self.assertIn(anchor['quote'], result)
        self.assertIn(f['test'], result)
        self.assertNotIn(f['fix'], result)
        f['proposal_anchors'] = [dict(a, quote='Несогласованный срок')]
        with self.assertRaises(ValueError):
            author_proposal(f)

    def test_external_rule_is_separate_from_the_document_quote(self):
        source = Path(__file__).parent / "fixtures" / "locker.md"
        doc = read_document(source)
        block = next(b for b in doc.blocks if b.source_id == "М-2")
        item = {"id": "R-fixture", "block": block.id, "quote": block.text,
                "section": block.section, "location": block.location}
        finding = {"id": "Z-001", "kind": "Рекомендация", "category": "Ясность",
                   "severity": "Низкая", "reason": "Проверить связь с внешним правилом.",
                   "counted": False, "ids": [item["id"]], "evidence": [item],
                   "scenario": "", "consequence": "", "interpretations": [], "fix": ""}
        result = {"requirements": [dict(item, summary="Время выдачи ключа", source_id="М-2",
                                        status="Есть рекомендация", assessment="Проверить время.",
                                        findings=["Z-001"])], "findings": [finding], "questions": [],
                  "counts": dict(requirements=1, defects=0, questions=0, gaps=0,
                                 ambiguities=0, recommendations=1),
                  "set_review": dict(assessment="Проверено.", readiness="Требуется уточнение.", priorities=[])}
        passport = dict(origin="Фикстура", started="", finished="", seconds=0., commit="abc",
                        state="чистая", provider="Фикстура", model="Фикстура")
        output = Path("reports") / "example.md"
        self.assertNotIn("Внешнее основание", render(doc, result, passport, source, output))
        rule = "Правило из внешнего справочника."
        finding["reference"] = dict(rule=rule, title="Учебная ссылка", url="https://example.org/reference")
        markdown = render(doc, result, passport, source, output)
        self.assertIn(f"**Внешнее основание.** {rule} [Учебная ссылка](https://example.org/reference)", markdown)
        self.assertFalse(any(rule in line for line in markdown.splitlines() if line.startswith("> ")))
