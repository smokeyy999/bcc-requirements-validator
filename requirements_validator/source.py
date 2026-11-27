"""Read-only source indexing with line and page anchors for exact quotations."""

import hashlib
import io
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Block:
    id: str
    text: str
    section: str
    source_id: str | None
    location: str
    kind: str
    page: int | None
    first_line: int
    last_line: int


@dataclass(frozen=True)
class Document:
    title: str
    sha256: str
    blocks: tuple[Block, ...]


_HEADING = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+(.*?))?[ \t]*$")
_SETEXT = re.compile(r" {0,3}(=+|-+)[ \t]*")
_FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
_ITEM = re.compile(r"^\s*(?:[-+*]\s+|\d+(?:\.\d+)*[.)]\s+)")
_EXPLICIT_ID = re.compile(
    r"^\s*(?:[-+*]\s+)?[*_`\[]*"
    r"([A-Za-zА-Яа-яЁё][\w]*(?:[-‐‑–.]\d+)+(?:[-.]\w+)*?)"
    r"(?=[.:)*_`\]\s]|$)"
)
_ORDINAL = re.compile(r"^\s*[*_]*(\d+(?:\.\d+)*)(?:[.)]|\*\*)(?=\s|[*_]|$)")


def _source_id(line):
    for pattern in (_EXPLICIT_ID, _ORDINAL):
        match = pattern.match(line)
        if match:
            return match[1]
    return None


def _cells(line):
    return [c.strip() for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]


def _table_separator(line):
    return "|" in line and all(re.fullmatch(r":?-{3,}:?", c) for c in _cells(line))


def _rule(line):
    return bool(re.fullmatch(r" {0,3}(?:(?:-\s*){3,}|(?:\*\s*){3,}|(?:_\s*){3,})", line))


def _index_page(text, page, headings, blocks, styled_headings=None):
    # keepends preserves LF/CRLF inside multiline source quotations.
    lines = text.splitlines(keepends=True)
    content = [line.rstrip("\r\n") for line in lines]
    title = None
    i = 0
    table_header = None
    styled_headings = styled_headings or {}

    def heading_at(raw):
        marked = _HEADING.match(raw)
        if marked:
            name = re.sub(r"(?:^|[ \t]+)#+$", "", marked[2] or "").strip()
            return len(marked[1]), name
        return styled_headings.get(raw.strip())

    def layout_cells(raw):
        # A native PDF has no pipe characters. Retain visible column boundaries
        # from pypdf's positional layout; a spaced paragraph is still quoted verbatim.
        return re.split(r"\s{2,}", raw.strip()) if page else []

    def emit(start, end, kind, explicit_id=None):
        section = " / ".join(h for _, h in headings) or "Начало документа"
        if table_header and kind == "table":
            section += " / Столбцы: " + " · ".join(table_header)
        first, last = start + 1, end
        span = str(first) if first == last else f"{first}–{last}"
        label = f"строка {span}" if first == last else f"строки {span}"
        anchor, loc = f"M{first:04}", label
        if page is not None:
            anchor, loc = f"P{page:03}L{first:04}", f"PDF, стр. {page}, {label} текстового слоя"
        quote = "".join(lines[start:end]).rstrip("\r\n")
        blocks.append(Block(anchor, quote, section, explicit_id, loc,
                            kind, page, first, last))

    def emit_heading(depth, name, start, end):
        nonlocal title, table_header
        table_header = None
        while headings and headings[-1][0] >= depth:
            headings.pop()
        if name:
            headings.append((depth, name))
            if depth == 1 and title is None:
                title = name
            emit(start, end, "heading", _source_id(name))

    while i < len(lines):
        raw = content[i]
        stripped = raw.strip()
        if not stripped or _rule(raw):
            table_header = None
            i += 1
            continue
        heading = heading_at(raw)
        if heading:
            emit_heading(*heading, i, i + 1)
            i += 1
            continue
        fence = _FENCE.match(raw)
        if fence:
            mark = fence[1]
            end = i + 1
            while end < len(lines):
                candidate = content[end].strip()
                end += 1
                if len(candidate) >= len(mark) and set(candidate) == {mark[0]}:
                    break
            emit(i, end, "code")
            i, table_header = end, None
            continue
        is_header = "|" in raw and i + 1 < len(lines) and _table_separator(content[i + 1])
        if is_header:
            table_header, i = _cells(raw), i + 2
            continue
        if stripped.startswith("|") or (table_header and "|" in raw):
            identifier = None
            if table_header:
                for column, cell in zip(table_header, _cells(raw)):
                    if column.casefold() in {"id", "идентификатор", "код требования", "requirement id", "id требования", "№"}:
                        identifier = cell.strip("*_` ") or None
                        break
            emit(i, i + 1, "table", identifier)
            i += 1
            continue
        columns = layout_cells(raw)
        if len(columns) >= 2:
            if table_header is None:
                table_header = columns
            emit(i, i + 1, "table")
            i += 1
            continue
        table_header = None
        explicit_id = _source_id(raw)
        item = _ITEM.match(raw)
        end = i + 1
        underline = None
        while end < len(lines):
            nxt = content[end]
            if page is None and not item and (underline := _SETEXT.fullmatch(nxt)):
                break
            if (not nxt.strip() or heading_at(nxt) or _FENCE.match(nxt)
                    or _ITEM.match(nxt) or _source_id(nxt) or _rule(nxt)
                    or nxt.strip().startswith("|")
                    or len(layout_cells(nxt)) >= 2
                    or ("|" in nxt and end + 1 < len(lines) and _table_separator(content[end + 1]))):
                break
            end += 1
        if underline:
            name = " ".join(line.strip() for line in content[i:end])
            depth = 1 if underline[1].startswith("=") else 2
            emit_heading(depth, name, i, end)
            i = end + 1
        else:
            emit(i, end, "item" if item else "text", explicit_id)
            i = end
    return title


def _pdf_pages(data):
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise ValueError("Для PDF установите зависимости: python -m pip install -r requirements.txt.") from exc
    try:
        reader = PdfReader(io.BytesIO(data))
        if reader.is_encrypted and not reader.decrypt(""):
            raise ValueError("Для чтения защищённого PDF передайте копию без пароля.")
        pages = []
        styled_lines = []
        sizes = {}
        unreadable = []
        for number, page in enumerate(reader.pages, 1):
            content = page.extract_text(extraction_mode="layout") or ""
            pages.append(content)
            if not content.strip():
                stream = page.get_contents()
                # Empty separator pages are permitted. A page which paints
                # graphics without extractable text may carry scanned requirements.
                paints = {b"Do", b"INLINE IMAGE", b"S", b"s", b"f", b"F", b"f*", b"B", b"b", b"B*", b"b*", b"sh", b"Tj", b"TJ"}
                if stream is not None and any(op in paints for _, op in stream.operations):
                    unreadable.append(number)
                continue
            if any(_HEADING.match(line) for line in content.splitlines()):
                continue

            def record(fragment, cm, tm, font, size):
                for line in fragment.splitlines():
                    line = line.strip()
                    if line:
                        sizes[size] = sizes.get(size, 0) + len(line)
                        styled_lines.append((number, line, size))

            page.extract_text(visitor_text=record)
        title = (reader.metadata.title or "").strip() if reader.metadata else ""
    except Exception as exc:
        if isinstance(exc, ValueError) and "без пароля" in str(exc):
            raise
        raise ValueError("Не удалось прочитать PDF. Проверьте файл или экспортируйте его заново.") from exc
    if unreadable or not any(p.strip() for p in pages):
        where = f" на страницах {', '.join(map(str, unreadable))}" if unreadable else ""
        raise ValueError(f"В PDF отсутствует текстовый слой{where}. Для скана выполните OCR, для пустых страниц удалите их.")
    heading_maps = [{} for _ in pages]
    if sizes:
        body = max(sizes, key=sizes.get)
        levels = sorted({size for size in sizes if size >= body * 1.15}, reverse=True)
        for number, line, size in styled_lines:
            if size in levels and len(line) <= 120 and not _source_id(line):
                heading_maps[number - 1][line] = (min(6, 1 + levels.index(size)), line)
    return pages, title, heading_maps


def read_document(path: Path) -> Document:
    path = Path(path)
    if not path.is_file():
        raise ValueError(f"Входной файл не найден. Проверьте путь: {path}")
    ext = path.suffix.casefold()
    if ext not in {".md", ".markdown", ".pdf", ".docx"}:
        raise ValueError("Неподдерживаемый формат. Передайте Markdown (.md, .markdown), PDF или DOCX.")
    try:
        if ext == ".docx" and path.stat().st_size > 64 * 1024 * 1024:
            raise ValueError("Файл DOCX превышает 64 МиБ. Сохраните текстовую копию без крупных вложений.")
        data = path.read_bytes()
    except OSError as exc:
        raise ValueError("Не удалось прочитать файл. Проверьте права доступа.") from exc
    if not data.strip():
        raise ValueError("Входной файл пуст. Выберите заполненный документ.")
    digest = hashlib.sha256(data).hexdigest()
    pdf_title = ""
    if ext == ".docx":
        from .docx_source import index_docx
        title, blocks = index_docx(data)
        if not blocks:
            raise ValueError("В DOCX нет текста для анализа. Для скана выполните OCR и сохраните текст в документе.")
        return Document(title or path.stem, digest, tuple(blocks))
    if ext == ".pdf":
        pages, pdf_title, heading_maps = _pdf_pages(data)
    else:
        try:
            decoded = data.decode("utf-8-sig")
            if "\x00" in decoded:
                raise UnicodeError()
        except UnicodeError as exc:
            raise ValueError("Markdown должен содержать текст UTF-8. Проверьте формат и кодировку.") from exc
        pages, heading_maps = [decoded], [{}]
    blocks, headings = [], []
    document_title = None
    for number, page_text in enumerate(pages, 1):
        title = _index_page(page_text, number if ext == ".pdf" else None, headings, blocks, heading_maps[number - 1])
        document_title = document_title or title
    if not blocks:
        raise ValueError("Документ не содержит текста для анализа. Передайте содержательную спецификацию.")
    return Document(document_title or pdf_title or path.stem, digest, tuple(blocks))
