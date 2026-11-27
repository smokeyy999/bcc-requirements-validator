"""Offline fixtures for document parsing; no organizer findings are injected."""

import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

from requirements_validator.engine import review
from requirements_validator.source import read_document


class SourceTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.folder = Path(folder.name)

    def write(self, name, content):
        path = self.folder / name
        path.write_bytes(content)
        return path

    def pdf(self, streams):
        doc = PdfWriter()
        for program in streams:
            page = doc.add_blank_page(width=500, height=500)
            if program:
                font = DictionaryObject({NameObject("/Type"): NameObject("/Font"),
                                         NameObject("/Subtype"): NameObject("/Type1"),
                                         NameObject("/BaseFont"): NameObject("/Helvetica")})
                page[NameObject("/Resources")] = DictionaryObject({
                    NameObject("/Font"): DictionaryObject({NameObject("/F1"): font})
                })
                stream = DecodedStreamObject()
                stream.set_data(program)
                page[NameObject("/Contents")] = stream
        path = self.folder / "fixture.pdf"
        doc.write(path)
        return path

    def test_markdown_byte_hash_locations_sections_and_ids(self):
        rows = [
            "# Сад", "## Полив", "* **Р-17.** Полить клумбу", "  до заката.", "",
            "| ID | Вода |", "| :--- | ---: |", "| W-4 | 2 л |", "",
            "### Формат", "```json", '{"litres":2}', "```",
        ]
        raw = ("\r\n".join(rows) + "\r\n").encode("utf-8-sig")
        path = self.write("сад.md", raw)
        result = read_document(path)
        self.assertEqual(result.sha256, hashlib.sha256(raw).hexdigest())
        self.assertEqual(result.title, "Сад")
        title, section, item, table, formatting, code = result.blocks
        self.assertEqual([b.kind for b in (title, section, formatting)], ["heading"] * 3)
        self.assertEqual(item.source_id, "Р-17")
        self.assertEqual(item.location, "строки 3–4")
        self.assertEqual(item.text, "\r\n".join(rows[2:4]))
        self.assertEqual(item.section, "Сад / Полив")
        self.assertEqual((table.source_id, table.text), ("W-4", rows[7]))
        self.assertIn("ID · Вода", table.section)
        self.assertEqual(code.text, "\r\n".join(rows[10:]))
        self.assertIsNone(code.source_id)
        self.assertEqual(result.blocks, read_document(path).blocks)

    def test_unchecked_rows_and_differently_scoped_list_numbers(self):
        text = ("# Фестиваль\n## Сцена\n1. Проверить свет.\n## Вход\n"
                "1. Проверить билеты.\n\nКто | Подпись\n--- | ---\n | |\n")
        blocks = read_document(self.write("test.md", text.encode())).blocks
        self.assertEqual([b.source_id for b in blocks], [None, None, "1", None, "1", None])
        self.assertNotEqual(blocks[2].section, blocks[4].section)
        self.assertEqual(blocks[-1].text, " | |")

    def test_input_diagnostics(self):
        with self.assertRaisesRegex(ValueError, "не найден"):
            read_document(self.folder / "missing.md")
        for name, data, pattern in [
            ("empty.md", b"\n  \t", "пуст"),
            ("corrupt.md", b"\xff", "UTF-8"),
            ("binary.md", b"abc\x00abc", "UTF-8"),
            ("headings.md", b"#\n----\n", "не содержит текста"),
            ("other.txt", b"hello", "Неподдерживаемый"),
            ("corrupt.pdf", b"%PDF-1.4\ncut", "прочитать PDF"),
        ]:
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, pattern):
                read_document(self.write(name, data))

    def test_rules_in_atx_and_setext_headings_keep_their_own_citations(self):
        lines = ["# Доступ", "## REQ-1. Блокировка через минуту",
                 "## Авторизация", "Карта открывает проход.", "",
                 "REQ-2. При тревоге", "турникет открыт", "-------",
                 "## Проход только по карте ###"]
        source = self.write("turnstile.md", ("\r\n".join(lines) + "\r\n").encode())
        title, first, section, body, multi, last = read_document(source).blocks
        self.assertEqual((first.id, first.source_id, first.kind, first.text),
                         ("M0002", "REQ-1", "heading", lines[1]))
        self.assertEqual(body.section, "Доступ / Авторизация")
        self.assertEqual((multi.id, multi.source_id, multi.text, multi.location),
                         ("M0006", "REQ-2", "\r\n".join(lines[5:7]), "строки 6–7"))
        self.assertEqual((last.id, last.source_id, last.text, last.section),
                         ("M0009", None, lines[8], "Доступ / Проход только по карте"))
        self.assertEqual([b.kind for b in (title, section, multi, last)], ["heading"] * 4)

    def test_only_context_headings_stop_after_classification(self):
        document = read_document(self.write("heading.md", b"# Heading\n----\n"))
        provider = Mock(extract_workers=1)
        provider.ask.return_value = {"claims": [], "context": [{"block": "M0001", "role": "контекст"}]}
        with self.assertRaisesRegex(ValueError, "заголовки разделов без проверяемых требований"):
            review(document, provider)
        provider.ask.assert_called_once()

    def test_blank_and_unreadable_pdf_pages(self):
        with self.assertRaisesRegex(ValueError, "текстовый слой"):
            read_document(self.pdf([None]))
        with self.assertRaisesRegex(ValueError, "страницах 2"):
            read_document(self.pdf([b"BT /F1 10 Tf 10 400 Td (Paint gate) Tj ET",
                                    b"0 0 10 10 re f"]))

    def test_native_pdf_layout_and_font_heading(self):
        path = self.pdf([None,
                         b"BT /F1 18 Tf 20 450 Td (Garden) Tj ET "
                         b"BT /F1 10 Tf 20 415 Td (R-7. Use two litres for each plant.) Tj ET "
                         b"BT /F1 10 Tf 20 390 Td (Use the reserve tank before opening the main supply.) Tj ET"])
        document = read_document(path)
        self.assertEqual(document.title, "Garden")
        heading, item = document.blocks[:2]
        self.assertEqual((heading.kind, heading.page, heading.text.strip()), ("heading", 2, "Garden"))
        self.assertEqual((item.source_id, item.page, item.section), ("R-7", 2, "Garden"))
        self.assertIn("PDF, стр. 2", item.location)
        self.assertIn("two litres", item.text)

    def test_styled_pdf_heading_with_rule_keeps_page_and_literal_text(self):
        path = self.pdf([b"BT /F1 18 Tf 20 450 Td (Use the emergency exit) Tj ET "
                         b"BT /F1 10 Tf 20 400 Td (The lower level contains the main room and the gate.) Tj ET"])
        heading, body = read_document(path).blocks
        self.assertEqual((heading.kind, heading.page, heading.text.strip()), ("heading", 1, "Use the emergency exit"))
        self.assertEqual(heading.location, f"PDF, стр. 1, строка {heading.first_line} текстового слоя")
        self.assertEqual(body.section, "Use the emergency exit")


if __name__ == "__main__":
    unittest.main()
