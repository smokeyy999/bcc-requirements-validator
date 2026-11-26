"""Build a native Word copy of the organizer fixture and verify its text and locations.

The fixture builder additionally needs python-docx==1.2.0. The CLI reader uses
only the Python standard library for DOCX files.
"""

import argparse
import re
from pathlib import Path

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from docx.table import Table
from docx.text.paragraph import Paragraph

from requirements_validator.source import read_document


def visible(text):
    return text.replace("**", "").replace("`", "").strip()


def source_items(path):
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    pos = 0
    while pos < len(lines):
        line = lines[pos].strip()
        pos += 1
        if not line or line == "---":
            continue
        if line.startswith("|"):
            rows = [line]
            while pos < len(lines) and lines[pos].strip().startswith("|"):
                rows.append(lines[pos].strip())
                pos += 1
            cells = [[visible(c) for c in row.strip("|").split("|")] for row in rows]
            yield "table", [row for row in cells if not all(re.fullmatch(r":?-+:?", c) for c in row)]
        elif line.startswith("```"):
            start = pos
            while pos < len(lines) and not lines[pos].startswith("```"):
                pos += 1
            yield "Code", "\n".join(lines[start:pos])
            pos += 1
        elif line.startswith("#"):
            mark, value = line.split(" ", 1)
            yield "Title" if len(mark) == 1 else f"Heading {len(mark) - 1}", visible(value)
        else:
            yield "Normal", visible(line.removeprefix("* "))


def make_copy(source, target):
    doc = Document()
    section = doc.sections[0]
    section.page_width, section.page_height = Cm(21), Cm(29.7)
    section.left_margin = section.right_margin = Cm(1.75)
    section.top_margin = section.bottom_margin = Cm(1.7)
    normal = doc.styles["Normal"]
    normal.font.name, normal.font.size = "Calibri", Pt(10.5)
    normal.paragraph_format.space_after = Pt(3)
    title = doc.styles["Title"]
    for border in title.element.xpath("./w:pPr/w:pBdr"):
        border.getparent().remove(border)
    for level in range(1, 5):
        heading = doc.styles[f"Heading {level}"].paragraph_format
        heading.space_before, heading.space_after = Pt(9), Pt(3)
    code = doc.styles.add_style("Code", WD_STYLE_TYPE.PARAGRAPH)
    code.font.name, code.font.size = "Consolas", Pt(9)
    for kind, value in source_items(source):
        if kind != "table":
            p = doc.add_paragraph(value, style=kind)
            if kind == "Title" or kind.startswith("Heading"):
                p.runs[0].font.color.rgb = RGBColor.from_string("000000" if kind == "Title" else "172F44")
            continue
        columns = len(value[0])
        table = doc.add_table(rows=0, cols=columns)
        table.style = "Table Grid"
        table.autofit = False
        if columns == 4:
            shares = [.49, .16, .12, .23]
        elif columns == 2:
            shares = [.31, .69]
        elif columns == 7:
            shares = [.13, .10, .11, .13, .18, .23, .12]
        else:
            shares = [1 / columns] * columns
        for col, share in zip(table.columns, shares):
            col.width = Cm(17.5 * share)
        for number, values in enumerate(value):
            row = table.add_row()
            props = row._tr.get_or_add_trPr()
            props.append(OxmlElement("w:cantSplit"))
            if number == 0:
                props.append(OxmlElement("w:tblHeader"))
            for cell, field, share in zip(row.cells, values, shares):
                cell.width = Cm(17.5 * share)
                p = cell.paragraphs[0]
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.space_before = Pt(2)
                run = p.add_run(field)
                run.font.size, run.bold = Pt(9), number == 0
                if number == 0:
                    shade = OxmlElement("w:shd")
                    shade.set(qn("w:fill"), "DFEAF1")
                    cell._tc.get_or_add_tcPr().append(shade)
    doc.core_properties.title = read_document(source).title
    doc.core_properties.author = "BCC validator"
    target.parent.mkdir(parents=True, exist_ok=True)
    doc.save(target)


def verify(source, target):
    doc = Document(target)
    body, paragraphs, rows = [], {}, {}
    paragraph_number = table_number = 0
    for item in doc.element.body:
        if item.tag == qn("w:p"):
            p = Paragraph(item, doc)
            paragraph_number += 1
            body.append((p.style.name, p.text))
            paragraphs[f"D{paragraph_number:04}"] = p.text
        elif item.tag == qn("w:tbl"):
            table_number += 1
            grid = [[c.text for c in r.cells] for r in Table(item, doc).rows]
            body.append(("table", grid))
            for i, values in enumerate(grid, 1):
                rows[f"T{table_number:03}R{i:04}"] = "\t".join(values)
    if list(source_items(source)) != body:
        raise ValueError("Содержимое DOCX отличается от абзацев, примеров или таблиц оригинала.")
    indexed = read_document(target)
    expected_ids = [b.source_id for b in read_document(source).blocks if b.source_id]
    actual_ids = [b.source_id for b in indexed.blocks if b.source_id]
    if actual_ids != expected_ids:
        raise ValueError("Нарушен порядок идентификаторов требований.")
    for block in indexed.blocks:
        if block.text != (rows if block.kind == "table" else paragraphs).get(block.id):
            raise ValueError(f"Неверная привязка: {block.location}")
    semantic = {k: sum(b.kind == k for b in indexed.blocks) for k in {"table", "code"}}
    print(f"DOCX: paragraphs={paragraph_number}, tables={table_number}, "
          f"data_rows={semantic['table']}, code={semantic['code']}, "
          f"source_ids={len(actual_ids)}, verified_locators={len(indexed.blocks)}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    if not args.verify_only:
        make_copy(args.input, args.output)
    verify(args.input, args.output)
