"""Create a searchable typographic copy of the Markdown and check its anchors.

Requires the optional reportlab package and a TrueType font covering the input.
Use a scratch directory for the PDF. The CLI report is generated from the original.
"""

import argparse
import re
from pathlib import Path

from pypdf import PdfReader
from reportlab.lib.pagesizes import A3, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas

from requirements_validator.source import read_document


def make_copy(source, target, font_path):
    text = source.read_text(encoding="utf-8-sig")
    font = TTFont("CopyFont", str(font_path))
    missing = sorted(c for c in set(text) if not c.isspace() and ord(c) not in font.face.charToGlyph)
    if missing:
        raise ValueError(f"Выбранный шрифт не содержит символов: {''.join(missing)}")
    pdfmetrics.registerFont(font)
    width, height = landscape(A3)
    margin, size, leading = 34, 10, 14
    longest = max(pdfmetrics.stringWidth(row, font.fontName, size) for row in text.splitlines())
    width = max(width, 2 * margin + longest)
    target.parent.mkdir(parents=True, exist_ok=True)
    document = Canvas(str(target), pagesize=(width, height), pageCompression=1)
    document.setTitle(read_document(source).title)
    y = height - margin

    def new_page():
        document.showPage()
        document.setFont(font.fontName, size)
        return height - margin

    document.setFont(font.fontName, size)
    for paragraph in re.split(r"\n\s*\n", text.strip()):
        rows = paragraph.splitlines()
        if len(rows) * leading <= height - 2 * margin and y - (len(rows) - 1) * leading < margin:
            y = new_page()
        for row in rows:
            if y < margin:
                y = new_page()
            document.drawString(margin, y, row)
            y -= leading
        y -= leading
    document.save()


def normalize(text):
    return " ".join(text.split())


def verify(source, target):
    original = read_document(source)
    extracted = read_document(target)
    reader = PdfReader(target)
    page_text = [p.extract_text(extraction_mode="layout") for p in reader.pages]
    # Independent stream of every token, including headings, table values and fences.
    if normalize(source.read_text(encoding="utf-8-sig")) != normalize("\n".join(page_text)):
        raise ValueError("Последовательность токенов исходника и PDF различается.")
    key = lambda block: (normalize(block.text), block.source_id, block.section, block.kind)
    if list(map(key, original.blocks)) != list(map(key, extracted.blocks)):
        raise ValueError("Сегментация, контекст или исходные ID различаются между форматами.")
    for block in extracted.blocks:
        lines = page_text[block.page - 1].splitlines()
        fragment = "\n".join(lines[block.first_line - 1:block.last_line])
        if fragment != block.text:
            raise ValueError(f"Цитата не совпадает с текстовым слоем: {block.location}")
    for kind in ("table", "code"):
        print(f"{kind}: {sum(b.kind == kind for b in extracted.blocks)}")
    example = next((b for b in extracted.blocks if b.kind == "code"), extracted.blocks[0])
    print(f"Проверено {len(page_text)} стр., блоков и локаторов: {len(extracted.blocks)}.")
    print(f"Совпали все токены и исходные ID ({sum(b.source_id is not None for b in extracted.blocks)} вхождений).")
    print(f"Пример: {example.id}, {example.location}, {example.section}")
    print(example.text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--font", type=Path, required=True)
    args = parser.parse_args()
    make_copy(args.input, args.output, args.font)
    verify(args.input, args.output)
