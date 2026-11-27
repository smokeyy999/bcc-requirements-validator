"""Проверка внешнего основания на коротком синтетическом примере."""
import re
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from requirements_validator.report import author_proposal, render
from requirements_validator.source import read_document
from scripts.verify_report import verify


class ReferenceRenderingTest(unittest.TestCase):
    def test_multiline_source_links_open_the_range_and_keep_archived_reports_readable(self):
        with TemporaryDirectory() as tmp:
            source = Path(tmp) / "card #1.md"
            source.write_bytes("Сервис возвращает номер\nв ответе на запрос.\n".encode())
            document = read_document(source)
            block, = document.blocks
            claim = dict(id="R-M0001-01", block=block.id, quote=block.text, section=block.section,
                         summary="Номер в ответе", source_id=None, status="Проверено",
                         assessment="Результат указан.", findings=[])
            counts = dict(requirements=1, defects=0, questions=0, gaps=0, ambiguities=0, recommendations=0)
            result = dict(requirements=[claim], questions=[], findings=[], counts=counts,
                          set_review=dict(readiness="Готово.", assessment="Проверено.", priorities=[]))
            run = dict(origin="Фикстура", started="", finished="", seconds=0., commit="abc",
                       state="чистая", provider="Фикстура", model="Фикстура")
            saved = Path(tmp) / "review.md"
            report = render(document, result, run, source, saved)
            self.assertIn("[строки 1–2](card%20%231.md?plain=1#L1-L2)", report)
            self.assertIn(r"[card \#1.md](card%20%231.md)", report)
            for location in ("?plain=1#L1-L2", "#L1"):
                saved.write_text(report.replace("?plain=1#L1-L2", location), encoding="utf-8")
                self.assertEqual(1, verify(saved, source)["quotes"])
            saved.write_text(report.replace("#L1-L2", "#L1-L3"), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Диапазоны"):
                verify(saved, source)

    def test_agenda_groups_questions_and_routes_only_to_declared_contacts_in_scope(self):
        source_text = """# Мастерская
## Приём
### Паспорт документа
| Поле | Значение |
|---|---|
| Автор | Группа приёмки |
### Правила
Каждый заказ получает номер.
## Выпуск
### Паспорт документа
| Поле | Значение |
|---|---|
| Автор | Группа выпуска |
### Правила
Для выпуска нужен талон.
"""
        with TemporaryDirectory() as tmp:
            source = Path(tmp) / "spec.md"
            source.write_text(source_text, encoding="utf-8")
            doc = read_document(source)
            a, b = (next(block for block in doc.blocks if block.text == text)
                    for text in ("Каждый заказ получает номер.", "Для выпуска нужен талон."))
            claims, findings, questions = [], [], []
            for i, (block, severity, counted, blocking) in enumerate((
                    (a, "Низкая", False, False), (b, "Существенная", False, False),
                    (b, "Существенная", True, False), (a, "Критичная", True, True)), 1):
                rule_id, ident = f"R-M000{i}-01", f"Z-{i:03}"
                ev = dict(id=rule_id, block=block.id, section=block.section, location=block.location, quote=block.text)
                claims.append(dict(ev, summary=block.text, source_id=None, status="Проверено", assessment="Есть вопрос.",
                                   findings=[ident], resolution_sources=[]))
                findings.append(dict(id=ident, ids=[rule_id], kind="Дефект" if counted else "Предполагаемый пробел",
                                     topic=f"Тема {i}", category="Полнота", severity=severity, reason="Причина.", counted=counted,
                                     evidence=[ev], scenario="Проверить.", consequence="", interpretations=[], fix=""))
                questions.append(dict(question=f"Вопрос {i}?", test=f"Тест {i}.", findings=[ident, ident], blocking=blocking))
            claims[0]["resolution_sources"] = [claims[0]["id"], claims[1]["id"], claims[1]["id"]]
            result = dict(requirements=claims, questions=questions, findings=findings,
                          counts=dict(requirements=4, defects=2, questions=4, gaps=2, ambiguities=0, recommendations=0),
                          set_review=dict(readiness="Готовность.", assessment="Проверено.", priorities=["Согласовать Z-004."]))
            run = dict(origin="Фикстура", started="", finished="", seconds=0., commit="abc",
                       state="чистая", provider="Фикстура", model="Фикстура")
            output = render(doc, result, run, source, source.with_suffix(".report.md"))
            agenda = output.split("## Вопросы к автору ТЗ", 1)[1].split('<a id="findings">', 1)[0]
            self.assertEqual(["4", "3", "2", "1"], re.findall(r"\*\*Вопрос (\d)\?\*\*", agenda))
            for i, contact in enumerate(("Группа приёмки", "Группа выпуска", "Группа выпуска", "Группа приёмки"), 1):
                item = agenda.split(f"**Вопрос {i}?**")[1].split("###")[0]
                target = re.search(r"Роли в связанных разделах ТЗ — \[Автор\]\(#([^)]+)\)", item)[1]
                self.assertIn(f"Тест {i}.", item)
                self.assertEqual(item.count(f"[Z-{i:03}](#z-{i:03})"), 1)
                scope = agenda.split(f'<a id="{target}"></a>')[1].split("\n\n", 2)[1]
                self.assertIn(contact, scope)
                self.assertRegex(scope, r"\[строка (\d+)\]\(spec.md\?plain=1#L\1\)")
            self.assertIn("1. Согласовать [Z-004](#z-004).", output)
            self.assertIn("Основания для снятия замечания — [R-M0002-01](#r-m0002-01).", output)

    def test_document_fix_checks_the_corrected_rule_instead_of_repeating_the_problem(self):
        anchor = dict(id="R-M0001-01", quote="Лимит посетителей указан в разделе «Часы работы».")
        finding = dict(counted=True, evidence=[anchor], ids=[anchor["id"]], proposal_options=[],
                       fix="Поместить лимит в раздел «Вместимость».",
                       scenario="Читатель находит лимит в разделе «Часы работы».", test="")
        for rule in (None, dict(rule="Заголовок раздела должен обозначать его содержание.")):
            with self.subTest(rule=rule):
                finding["reference"] = rule
                test = author_proposal(finding)[-1]
                self.assertIn(anchor["id"], test)
                self.assertIn(rule["rule"] if rule else finding["fix"], test)
                self.assertNotIn(finding["scenario"], test)
        finding["test"] = "Открыть раздел по новому названию и прочитать лимит."
        self.assertIn(finding["test"], author_proposal(finding)[-1])

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
