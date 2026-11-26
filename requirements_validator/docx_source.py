"""Index the main Word story in reading order without extracting files to disk."""

import io
import re
import zipfile
from xml.etree import ElementTree as ET

from .source import Block, _source_id


WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
STRICT_NS = "http://purl.oclc.org/ooxml/wordprocessingml/main"
W = "{" + WORD_NS + "}"
LIMIT = 16 * 1024 * 1024
ID_COLUMNS = {"id", "идентификатор", "код требования", "requirement id", "id требования", "№"}


class _WordTree(ET.TreeBuilder):
    def doctype(self, name, pubid, system):
        raise ValueError("DOCX содержит неподдерживаемое объявление DTD. Сохраните обычный документ Word.")


def _read_xml(archive, path):
    info = archive.getinfo(path)
    if info.file_size > LIMIT:
        raise ValueError("Текстовая часть DOCX превышает 16 МиБ. Разделите документ на части.")
    with archive.open(info) as stream:
        data = stream.read(LIMIT + 1)
    if len(data) > LIMIT:
        raise ValueError("Превышен предел распаковки текстовой части DOCX.")
    root = ET.fromstring(data, parser=ET.XMLParser(target=_WordTree()))
    if root.tag.startswith("{" + STRICT_NS + "}"):
        for node in root.iter():
            node.tag = node.tag.replace(STRICT_NS, WORD_NS)
            node.attrib = {k.replace(STRICT_NS, WORD_NS): v for k, v in node.attrib.items()}
    return root


def _value(node, child):
    element = node.find(child)
    return element.get(W + "val", "") if element is not None else ""


def _style_map(styles):
    result = {}
    if styles is not None:
        for style in styles.findall(W + "style"):
            result[style.get(W + "styleId", "")] = (
                _value(style, W + "name"), _value(style, W + "pPr/" + W + "outlineLvl"),
                _value(style, W + "basedOn"))
    return result


def _classify(p, styles):
    direct = _value(p, W + "pPr/" + W + "outlineLvl")
    style = _value(p, W + "pPr/" + W + "pStyle")
    visited = set()
    while True:
        name, inherited, parent = styles.get(style, ("", "", ""))
        outline = direct or inherited
        if outline and outline.isdigit():
            level = int(outline)
            return ("heading", level + 1) if level < 9 else ("text", 0)
        for label in (name, style):
            if label.casefold() in {"title", "название", "заглавие"}:
                return "heading", 0
            match = re.fullmatch(r"(?:heading|заголовок)\s*([1-9])", label, re.I)
            if match:
                return "heading", int(match[1])
            if label.casefold() in {"code", "sourcecode", "source code", "код"}:
                return "code", 0
        if not parent or parent in visited:
            return "text", 0
        visited.add(style)
        style = parent


def _text(p):
    chunks = []
    def visit(node):
        if node.tag in {W + "del", W + "moveFrom", W + "pPr", W + "drawing", W + "pict"}:
            return
        if node.tag == W + "t":
            chunks.append(node.text or "")
        elif node.tag == W + "tab":
            chunks.append("\t")
        elif node.tag in {W + "br", W + "cr"}:
            chunks.append("\n")
        else:
            for child in node:
                visit(child)
    visit(p)
    return "".join(chunks)


def _children(node, tags):
    """Preserve document order through block-level content controls/revisions."""
    for child in node:
        if child.tag in tags:
            yield child
        elif child.tag in {W + "sdt", W + "sdtContent", W + "ins", W + "customXml", W + "moveTo"}:
            yield from _children(child, tags)
        elif child.tag == W + "altChunk":
            raise ValueError("DOCX содержит вложенную внешнюю часть. Откройте и пересохраните документ в Word.")


def index_docx(data):
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            names = archive.namelist()
            if len(names) > 10000 or len(names) != len(set(names)):
                raise ValueError("В DOCX превышено число частей или повторяются имена частей.")
            body = _read_xml(archive, "word/document.xml").find(W + "body")
            styles = _style_map(_read_xml(archive, "word/styles.xml") if "word/styles.xml" in names else None)
    except (zipfile.BadZipFile, KeyError, RuntimeError, ET.ParseError, OSError, NotImplementedError) as exc:
        raise ValueError("Не удалось прочитать DOCX. В Word сохраните исправную копию без пароля.") from exc
    if body is None:
        raise ValueError("В DOCX отсутствует основной текст Word.")

    blocks, headings = [], []
    paragraph_no = table_no = 0
    title = ""
    try:
        for node in _children(body, {W + "p", W + "tbl"}):
            section = " / ".join(h for _, h in headings) or "Начало документа"
            if node.tag == W + "p":
                paragraph_no += 1
                text = _text(node)
                if not text.strip():
                    continue
                kind, depth = _classify(node, styles)
                if kind == "heading":
                    while headings and headings[-1][0] >= depth:
                        headings.pop()
                    headings.append((depth, text.strip()))
                    if not title:
                        title = text.strip()
                    continue
                identifier = _source_id(text) or (text.strip() if re.fullmatch(r"\d+", text.strip()) else None)
                blocks.append(Block(f"D{paragraph_no:04}", text, section, identifier,
                                    f"DOCX, абзац {paragraph_no}", kind, None, paragraph_no, paragraph_no))
                continue

            table_no += 1
            header = []
            look = node.find(W + "tblPr/" + W + "tblLook")
            first_row_style = look is not None and look.get(W + "firstRow") in {"1", "on", "true"}
            for row_no, row in enumerate(_children(node, {W + "tr"}), 1):
                values = []
                for cell in _children(row, {W + "tc"}):
                    paragraphs = []
                    for item in _children(cell, {W + "p", W + "tbl"}):
                        if item.tag == W + "tbl":
                            raise ValueError("В DOCX есть вложенная таблица. Разместите её отдельно и повторите проверку.")
                        paragraphs.append(_text(item))
                    values.append("\n".join(paragraphs))
                marker = row.find(W + "trPr/" + W + "tblHeader")
                if marker is not None and marker.get(W + "val", "1") not in {"0", "off", "false"}:
                    header = values
                    continue
                if not any(v.strip() for v in values):
                    continue
                identifier = next((v.strip() for h, v in zip(header, values)
                                   if h.strip().casefold() in ID_COLUMNS), "") or _source_id(values[0])
                context = section + (" / Столбцы: " + " · ".join(header) if header else "")
                blocks.append(Block(f"T{table_no:03}R{row_no:04}", "\t".join(values),
                                    context, identifier, f"DOCX, таблица {table_no}, строка {row_no}",
                                    "table", None, row_no, row_no))
                if row_no == 1 and (first_row_style or any(v.strip().casefold() in ID_COLUMNS for v in values)):
                    header = values
    except RecursionError as exc:
        raise ValueError("Слишком глубокая вложенность текста DOCX. Пересохраните упрощённую копию.") from exc
    return title, blocks
