"""Представление проверенных данных. Все ссылки на источник вычисляются локально."""

import html
import os
import re
from pathlib import Path
from urllib.parse import quote


def plain(value):
    """Буквальное отображение текста из модели или документа в Markdown."""
    escaped = html.escape(str(value), quote=False)
    return re.sub(r"([\\`*_{}\[\]#|>~])", r"\\\1", escaped)


def cell(value):
    return " ".join(plain(value).splitlines())


def refs(ids):
    return ", ".join(f"[{item}](#{item.lower()})" for item in ids)


def render(doc, result, run, source_path, output_path):
    blocks = {b.id: b for b in doc.blocks}
    try:
        rel = Path(os.path.relpath(source_path.resolve(), output_path.resolve().parent))
        source_link = quote(rel.as_posix(), safe="/.")
    except ValueError:  # На Windows у путей могут быть разные диски.
        source_link = source_path.resolve().as_uri()

    def location(item):
        block = blocks[item["block"]]
        anchor = f"#page={block.page}" if block.page else f"#L{block.first_line}"
        return f'{plain(item["section"])} · [{plain(item["location"])}]({source_link}{anchor})'

    def evidence(item):
        lines = plain(item["quote"]).splitlines()
        return f'{location(item)}\n\n' + "\n".join(f"> {line}  " for line in lines)

    counts = result["counts"]
    findings = result["findings"]
    critical = [f for f in findings if f["counted"] and f["severity"] == "Критичная"]
    summary = result["set_review"]
    parts = [
        f'# Статическое ревью · {plain(doc.title)}',
        f'**Проверено утверждений — {counts["requirements"]} · нарушений — {counts["defects"]} · '
        f'критичных дефектов — {len(critical)} · вопросов к автору — {counts["questions"]}.**',
        plain(summary["readiness"]),
        "[Критичные дефекты](#critical) · [Вопросы](#questions) · [Замечания](#findings) · "
        "[Соответствие ID](#mapping) · [Проверка каждого требования](#checks) · [Итог](#decision)",
        "## Паспорт прогона",
        "| Поле | Значение |\n|---|---|\n"
        f"| Документ | {cell(doc.title)} |\n"
        f"| Входной файл | [{cell(source_path.name)}]({source_link}) |\n"
        f'| Источник | {run["origin"]} |\n'
        f"| SHA-256 исходных байтов | `{doc.sha256}` |\n"
        f'| Начало / окончание | {run["started"]} / {run["finished"]} |\n'
        f'| Анализ и проверка данных | {run["seconds"]:.1f} с |\n'
        f'| Провайдер и модель | {cell(run["provider"])} · `{cell(run["model"])}` |\n'
        f'| Коммит реализации | `{run["commit"]}` |\n'
        f'| Рабочая копия при старте | {run["state"]} |',
        "## Проверка набора в целом", plain(summary["assessment"]),
        f'Открытых предполагаемых пробелов — {counts["gaps"]}. '
        f'Неоднозначностей — {counts["ambiguities"]}. Рекомендаций — {counts["recommendations"]}.',
        "Каждый ID утверждения учитывается один раз. В число нарушений входят подтверждённые дефекты "
        "и неоднозначности, для которых показаны две опирающиеся на текст трактовки с разными последствиями. "
        "Один и тот же конфликт имеет один ID при любом числе затронутых требований. "
        "Вопросы и рекомендации имеют отдельные счётчики.",
        '<a id="critical"></a>\n\n## Критичные дефекты',
    ]
    parts.append("\n".join(f'- {refs([f["id"]])} · {plain(f["reason"])}' for f in critical)
                 or "Критичных дефектов не выявлено.")
    parts.append('<a id="questions"></a>\n\n## Вопросы к автору ТЗ')
    for q in sorted(result["questions"], key=lambda item: not item["blocking"]):
        prefix = "Блокирует приёмку" if q["blocking"] else "Требует уточнения"
        parts.extend([f'**{plain(q["question"])}**', f'{prefix} · {refs(q["findings"])}. '
                      f'Зависимый сценарий — {plain(q["test"])}'])
    if not result["questions"]:
        parts.append("Открытых вопросов по результатам проверки нет.")
    parts.append('<a id="findings"></a>\n\n## Реестр замечаний')
    for f in findings:
        parts.extend([f'<a id="{f["id"].lower()}"></a>\n\n### {f["id"]} · {plain(f.get("topic") or f["category"])}',
                      f'**{plain(f["kind"])} · {plain(f["category"])} · {plain(f["severity"])}.** {plain(f["reason"])}',
                      "Затронутые утверждения — " + refs(f["ids"]) + "."])
        for ev in f["evidence"]:
            parts.append(f'{refs([ev["id"]])} · {evidence(ev)}')
        reference = f.get("reference")
        if reference:
            parts.append(f'**Внешнее основание.** {plain(reference["rule"])} '
                         f'[{plain(reference["title"])}]({reference["url"]})')
        for field, label in (("scenario", "Сценарий"), ("consequence", "Последствие")):
            if f[field]:
                parts.append(f'**{label}.** {plain(f[field])}')
        if f["interpretations"]:
            parts.append("\n".join(f'{i}. {plain(t)}' for i, t in enumerate(f["interpretations"], 1)))
        if f["fix"]:
            parts.append("**Исправление по тексту документа.** " + plain(f["fix"]))
    if not findings:
        parts.append("Замечаний по результатам проверки нет.")
    parts.append('<a id="mapping"></a>\n\n## Таблица соответствия')
    table = ["| ID в отчёте | ID в исходном документе | Краткая формулировка |", "|---|---|---|"]
    for r in result["requirements"]:
        table.append(f'| {refs([r["id"]])} | {cell(r["source_id"] or "—")} | {cell(r["summary"])} |')
    parts.extend(["\n".join(table), '<a id="checks"></a>\n\n## Проверка каждого требования'])
    for r in result["requirements"]:
        parts.extend([f'<a id="{r["id"].lower()}"></a>\n\n### {r["id"]} · {plain(r["summary"])}',
                      evidence(r), f'**{plain(r["status"])}.** {plain(r["assessment"])}'])
        if r["findings"]:
            parts.append("Связанные замечания — " + refs(r["findings"]) + ".")
    parts.extend(['<a id="decision"></a>\n\n## Готовность и порядок исправлений', plain(summary["readiness"])])
    if summary["priorities"]:
        parts.append("\n".join(f'{i}. {plain(t)}' for i, t in enumerate(summary["priorities"], 1)))
    return "\n\n".join(parts) + "\n"
