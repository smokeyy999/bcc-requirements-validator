"""Offline fixtures for document parsing; no organizer findings are injected."""

import hashlib
import tempfile
import unittest
from pathlib import Path

from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

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
        item, table, code = result.blocks
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
        self.assertEqual([b.source_id for b in blocks], ["1", "1", None])
        self.assertNotEqual(blocks[0].section, blocks[1].section)
        self.assertEqual(blocks[-1].text, " | |")

    def test_input_diagnostics(self):
        with self.assertRaisesRegex(ValueError, "не найден"):
            read_document(self.folder / "missing.md")
        for name, data, pattern in [
            ("empty.md", b"\n  \t", "пуст"),
            ("corrupt.md", b"\xff", "UTF-8"),
            ("binary.md", b"abc\x00abc", "UTF-8"),
            ("headings.md", b"# Heading\n----\n", "не содержит текста"),
            ("other.txt", b"hello", "Неподдерживаемый"),
            ("corrupt.pdf", b"%PDF-1.4\ncut", "прочитать PDF"),
        ]:
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, pattern):
                read_document(self.write(name, data))

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
        item = document.blocks[0]
        self.assertEqual((item.source_id, item.page, item.section), ("R-7", 2, "Garden"))
        self.assertIn("PDF, стр. 2", item.location)
        self.assertIn("two litres", item.text)


if __name__ == "__main__":
    unittest.main()
