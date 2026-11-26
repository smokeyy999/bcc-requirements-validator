"""Exercise native Word indexing with small offline fixtures from another domain."""

import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from zipfile import ZIP_DEFLATED, ZipFile

from requirements_validator.docx_source import WORD_NS
from requirements_validator.report import render
from requirements_validator.source import read_document


def p(text, properties=""):
    return f"<w:p>{properties}<w:r><w:t>{text}</w:t></w:r></w:p>"


def row(values, header=False):
    cells = "".join(f"<w:tc>{p(v)}</w:tc>" for v in values)
    marker = "<w:trPr><w:tblHeader/></w:trPr>" if header else ""
    return f"<w:tr>{marker}{cells}</w:tr>"


class WordSourceTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.path = Path(folder.name, "native.docx")

    def write(self, content, styles="", prolog=""):
        with ZipFile(self.path, "w", compression=ZIP_DEFLATED) as archive:
            archive.writestr("word/document.xml",
                             f'{prolog}<w:document xmlns:w="{WORD_NS}"><w:body>{content}</w:body></w:document>')
            if styles:
                archive.writestr("word/styles.xml", f'<w:styles xmlns:w="{WORD_NS}">{styles}</w:styles>')
        return read_document(self.path)

    def test_native_order_styles_and_coordinates(self):
        title = p("Архив", '<w:pPr><w:pStyle w:val="Title"/></w:pPr>')
        heading = p("Выдача", '<w:pPr><w:pStyle w:val="Local"/></w:pPr>')
        style = ('<w:style w:styleId="Local"><w:basedOn w:val="Base"/></w:style>'
                 '<w:style w:styleId="Base"><w:pPr><w:outlineLvl w:val="1"/></w:pPr></w:style>')
        item = '<w:p><w:r><w:t>А-2. Выдать </w:t></w:r><w:hyperlink><w:r><w:t>том.</w:t></w:r></w:hyperlink></w:p>'
        body = title + heading + item + "<w:tbl>" + row(["Код требования", "Срок"], True)
        body += row(["A-4", "48 часов"]) + "</w:tbl><w:sdt><w:sdtContent>" + p("Принять книгу.") + "</w:sdtContent></w:sdt>"
        result = self.write(body, style)
        self.assertEqual(result.title, "Архив")
        self.assertEqual(result.sha256, hashlib.sha256(self.path.read_bytes()).hexdigest())
        first, table, last = result.blocks
        self.assertEqual((first.id, first.location, first.source_id, first.text),
                         ("D0003", "DOCX, абзац 3", "А-2", "А-2. Выдать том."))
        self.assertEqual(table.section, "Архив / Выдача / Столбцы: Код требования · Срок")
        self.assertEqual((table.id, table.location, table.source_id, table.text),
                         ("T001R0002", "DOCX, таблица 1, строка 2", "A-4", "A-4\t48 часов"))
        self.assertEqual(last.id, "D0004")
        self.assertEqual(result.blocks, read_document(self.path).blocks)

    def test_unmarked_table_keeps_first_row_and_multiline_cell(self):
        cell = "<w:tc>" + p("Проверить.") + p("Опечатать.") + "</w:tc>"
        body = ("<w:tbl>" + row(["ID", "Условие"]) + "<w:tr><w:tc>" + p("R-4")
                + "</w:tc>" + cell + "</w:tr></w:tbl>")
        first, second = self.write(body).blocks
        self.assertEqual(first.text, "ID\tУсловие")
        self.assertEqual(second.source_id, "R-4")
        self.assertEqual(second.text, "R-4\tПроверить.\nОпечатать.")

    def test_empty_corrupt_and_over_limit(self):
        self.path.write_bytes(b"broken")
        with self.assertRaisesRegex(ValueError, "прочитать DOCX"):
            read_document(self.path)
        with self.assertRaisesRegex(ValueError, "нет текста"):
            self.write("<w:p/>")
        with self.assertRaisesRegex(ValueError, "DTD"):
            self.write(p("123"), prolog="<!DOCTYPE w:document>")
        with patch("requirements_validator.docx_source.LIMIT", 32), self.assertRaisesRegex(ValueError, "превышает"):
            self.write(p("Архив"))

    def test_deleted_text_not_quoted_and_nested_table_diagnosed(self):
        block, = self.write('<w:p><w:del><w:r><w:t>Было</w:t></w:r></w:del>'
                            '<w:ins><w:r><w:t>Стало</w:t><w:br/><w:t>Снова</w:t></w:r></w:ins></w:p>').blocks
        self.assertEqual(block.text, "Стало\nСнова")
        with self.assertRaisesRegex(ValueError, "вложенная таблица"):
            self.write("<w:tbl><w:tr><w:tc><w:tbl/></w:tc></w:tr></w:tbl>")

    def test_report_links_to_word_file_with_text_locator(self):
        document = self.write(p("Книга должна иметь шифр."))
        block, = document.blocks
        req = dict(id="R-D0001-01", block=block.id, quote=block.text, section=block.section,
                   location=block.location, summary="Шифр книги", source_id=None,
                   status="Проверяемо", assessment="Шифр можно проверить.", findings=[])
        result = dict(requirements=[req], findings=[], questions=[],
                      counts=dict(requirements=1, defects=0, questions=0, gaps=0, ambiguities=0, recommendations=0),
                      set_review=dict(assessment="Проверено.", readiness="Готово.", priorities=[]))
        passport = dict(origin="Фикстура", started="", finished="", seconds=0., commit="abc",
                        state="чистая", provider="Фикстура", model="Фикстура")
        output = render(document, result, passport, self.path, self.path.with_suffix(".md"))
        self.assertIn("[DOCX, абзац 1](native.docx)", output)
        self.assertNotIn("native.docx#", output)
