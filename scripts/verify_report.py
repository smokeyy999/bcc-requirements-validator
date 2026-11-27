"""Independent read-back check for the saved Markdown and its source links."""
import hashlib
import html
import re
from pathlib import Path
from urllib.parse import unquote


def markdown_location(line):
    address = re.search(
        r'\[строк[аи] (\d+)(?:–(\d+))?\]\(([^?#)\n]+)(\?plain=1)?#L(\d+)(?:-L(\d+))?\)$',
        line,
    )
    if not address:
        raise ValueError(f"Некорректная ссылка на строки Markdown: {line}")
    first, last, path, plain_view, anchor_first, anchor_last = address.groups()
    start = int(first)
    end = int(last or first)
    # Historical reports link to the first line of a labelled range.
    wrong_end = (plain_view or anchor_last) and int(anchor_last or anchor_first) != end
    if not 1 <= start <= end or int(anchor_first) != start or wrong_end:
        raise ValueError(f"Диапазоны в подписи и адресе Markdown расходятся: {line}")
    return path, start, end


def verify(report_path, doc_path):
    if not __debug__:
        raise ValueError("Проверку необходимо запускать без оптимизации -O")
    report = report_path.read_text(encoding="utf-8")
    source = doc_path.read_bytes()
    assert f"| SHA-256 исходных байтов | `{hashlib.sha256(source).hexdigest()}` |" in report
    if doc_path.suffix.lower() == ".pdf":
        from pypdf import PdfReader
        pages = [p.extract_text(extraction_mode="layout").splitlines() for p in PdfReader(doc_path).pages]
    elif doc_path.suffix.lower() == ".docx":
        from docx import Document
        word = Document(doc_path)
        word_paragraphs = [p.text for p in word.paragraphs]
        word_tables = [["\t".join(c.text for c in row.cells) for row in t.rows] for t in word.tables]
    else:
        pages = [source.decode("utf-8-sig").splitlines()]
    anchors = re.findall(r'<a id="([^"]+)"></a>', report)
    assert len(anchors) == len(set(anchors))
    for dest in re.findall(r'\]\(#([^)]*)\)', report):
        assert dest in anchors, dest
    requirements = re.findall(r'^### (R-[A-Z0-9]+-\d+) · ', report, re.M)
    mapping = re.findall(r'^\| \[(R-[A-Z0-9]+-\d+)\]', report, re.M)
    assert requirements == mapping
    edges = set()
    reverse_edges = set()
    for node, body in re.findall(r'^### ([ZR]-[^ ]+) · (.*?)(?=^<a id=|\Z)', report, re.M | re.S):
        if node.startswith("Z-"):
            affected = re.search(r'^Затронутые утверждения — (.+)$', body, re.M)[1]
            edges.update((node, ref) for ref in re.findall(r'\[(R-[^\]]+)\]', affected))
        else:
            linked = re.search(r'^Связанные замечания — (.+)$', body, re.M)
            if linked:
                reverse_edges.update((ref, node) for ref in re.findall(r'\[(Z-\d+)\]', linked[1]))
    assert edges == reverse_edges, edges ^ reverse_edges
    findings = re.findall(r'^### (Z-\d+) · .*?\n\n\*\*([^·]+) · ([^·]+) · ([^.]+)\.\*\*', report, re.M)
    dimension = lambda s: int(re.search(s + r' — (\d+)', report)[1])
    assert dimension("Проверено утверждений") == len(set(requirements))
    assert dimension("нарушений") == sum(kind in ("Дефект", "Неоднозначность") for _, kind, _, _ in findings)
    assert dimension("критичных дефектов") == sum(kind in ("Дефект", "Неоднозначность") and sev == "Критичная"
                                                for _, kind, _, sev in findings)
    for counter, kind in [("Открытых предполагаемых пробелов", "Предполагаемый пробел"),
                          ("Неоднозначностей", "Неоднозначность"), ("Рекомендаций", "Рекомендация")]:
        assert dimension(counter) == sum(category == kind for _, category, _, _ in findings)
    critical_section = report.split('## Критичные дефекты\n', 1)[1].split('<a id="questions">', 1)[0]
    assert set(re.findall(r'^- \[(Z-\d+)\]', critical_section, re.M)) == {
        node for node, kind, _, severity in findings if kind in ("Дефект", "Неоднозначность") and severity == "Критичная"}
    question_section = report.split("## Вопросы к автору ТЗ\n", 1)[1].split('<a id="findings">', 1)[0]
    questions = re.findall(r"^\*\*(.+?)\*\*$", question_section, re.M)
    assert len(set(questions)) == dimension("вопросов к автору") == len(questions)
    flags = re.findall(r'^(Блокирует приёмку|Требует уточнения) ·', question_section, re.M)
    assert len(flags) == len(questions) and flags == sorted(flags)
    saved = report.splitlines()
    seen = 0
    i = 0
    while i < len(saved):
        if not saved[i].startswith("> "):
            i += 1
            continue
        link = saved[i-2]
        if doc_path.suffix.lower() == ".docx":
            quoted_path = re.findall(r'\[DOCX, [^]]+\]\(([^)#]+)\)', link)
        elif doc_path.suffix.lower() == ".pdf":
            quoted_path = re.findall(r'\]\(([^)#]+)#page=\d+\)', link)
        else:
            path, first, end = markdown_location(link)
            quoted_path = [path]
        assert len(quoted_path) == 1 and (report_path.parent / unquote(quoted_path[0])).resolve() == doc_path.resolve(), link
        if doc_path.suffix.lower() == ".docx":
            paragraph = re.search(r'\[DOCX, абзац (\d+)\]', link)
            row = re.search(r'\[DOCX, таблица (\d+), строка (\d+)\]', link)
            assert bool(paragraph) != bool(row), link
            if paragraph:
                text = word_paragraphs[int(paragraph[1]) - 1]
            else:
                text = word_tables[int(row[1]) - 1][int(row[2]) - 1]
            page = text.splitlines()
            line_index, end = 0, len(page)
        elif doc_path.suffix.lower() == ".pdf":
            address = re.search(r'\[PDF, стр\. (\d+), строк[аи] (\d+)(?:–(\d+))? текстового слоя\]\([^)]*#page=(\d+)\)', link)
            assert address and address[1] == address[4], link
            page = pages[int(address[1])-1]
            line_index, end = int(address[2])-1, int(address[3] or address[2])
        else:
            page = pages[0]
            assert end <= len(page), link
            line_index = first - 1
        quote = []
        while i < len(saved) and saved[i].startswith("> "):
            quote.append(saved[i][2:].removesuffix("  "))
            i += 1
        unescaped = html.unescape(re.sub(r"\\([\\`*_{}\[\]#|>~])", r"\1", "\n".join(quote)))
        assert unescaped in "\n".join(page[line_index:end]), (line_index+1, unescaped)
        seen += 1
    assert seen >= len(requirements)

    return dict(requirements=len(requirements), findings=len(findings), questions=len(questions),
                critical_defects=dimension("критичных дефектов"), defects=dimension("нарушений"),
                blocking_questions=flags.count('Блокирует приёмку'), quotes=seen)


if __name__ == '__main__':
    import argparse
    import json
    parser = argparse.ArgumentParser(description='Независимая проверка готового отчёта по исходному документу.')
    parser.add_argument('report', type=Path)
    parser.add_argument('source', type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(verify(args.report, args.source), ensure_ascii=False, indent=2))
    except (AssertionError, ValueError, IndexError, OSError) as exc:
        parser.exit(1, f'Отчёт не прошёл проверку: {exc}\n')
