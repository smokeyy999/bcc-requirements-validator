"""Представление проверенных данных. Все ссылки на источник вычисляются локально."""

import html
import os
import re
from pathlib import Path
from urllib.parse import quote

from .text import text_key


def plain(value):
    """Буквальное отображение текста из модели или документа в Markdown."""
    escaped = html.escape(str(value), quote=False)
    return re.sub(r"([\\`*_{}\[\]#|>~])", r"\\\1", escaped)


def cell(value):
    return " ".join(plain(value).splitlines())


def refs(ids):
    return ", ".join(f"[{item}](#{item.lower()})" for item in ids)


def question_basis(finding):
    check = finding.get("question_basis")
    if not check:
        return []
    premise = finding.get("open_premise", {})
    shown = {text_key(finding.get(k, "")) for k in ("scenario", "consequence", "reason", "question", "test", "topic")}
    shown.update(text_key(premise.get(k, "")) for k in ("condition", "effect"))
    shown.update(text_key(option["effect"]) for option in finding.get("proposal_options", []))
    cited = list(dict.fromkeys([check["obligation_id"], *check["checked_ids"]]))
    lines = []
    for label, value in (("Уже установлено", check["known_answer"]), ("Открытое решение", check["decision"])):
        if text_key(value) not in shown:
            lines.append(f"**{label}.** {plain(value)}")
            shown.add(text_key(value))
    outcomes = [plain(value) for value in check["outcomes"] if text_key(value) not in shown]
    if outcomes:
        lines.append("**Что различит проверка.** " + " / ".join(outcomes))
    if lines:
        lines[0] += " Основания — " + refs(cited) + "."
    return lines


def _contacts(blocks):
    """Read explicit role/value fields in document metadata and retain their scope."""
    roles = {"автор", "автор тз", "аналитик", "владелец продукта", "бизнес-заказчик",
             "ответственный", "согласующий", "author", "business owner", "product owner", "owner"}
    metadata_headings = {"общие сведения", "общие параметры", "паспорт документа", "реквизиты",
                         "метаданные", "document metadata", "metadata", "document information"}
    contacts = []
    for block in blocks:
        if block.kind != "table":
            continue
        section, _, columns = block.section.partition(" / Столбцы:")
        headings = tuple(section.split(" / "))
        if headings[-1].casefold() in metadata_headings:
            scope = headings[:-1]
        elif len(headings) == 1 and columns.strip().casefold() in {"поле · значение", "field · value"}:
            scope = headings
        else:
            continue
        row = block.text.strip()
        fields = row.split("\t") if "\t" in row else row.strip("|").split("|")
        if len(fields) != 2:
            continue
        label, value = (part.strip().strip("*`").strip() for part in fields)
        if not all(role.strip() in roles for role in label.casefold().split("/")):
            continue
        if value.casefold() in {"", "-", "—", "–", "tbd", "n/a", "не указан", "не назначен", "не определён"}:
            continue
        contacts.append((scope, block, label, value))
    return contacts


def _question_stage(question, linked):
    if question["blocking"]:
        return 0
    if any(f["counted"] for f in linked):
        return 1
    if linked and all(f["severity"] == "Низкая" for f in linked):
        return 3
    return 2


def author_proposal(finding):
    """Keep each proposed choice next to its source and testable outcome."""
    if not finding["counted"]:
        return []
    evidence = finding["evidence"]
    test = plain(finding.get("test") or finding["scenario"])
    origin = ("Проверка ссылок по индексу исходного документа." if finding.get("missing_target")
              else "Предложение модели.")
    result = [f"**Предложение для автора.** {origin} Выбор формулировки и ожидаемого результата утверждает автор ТЗ."]
    options = finding.get("proposal_options", [])
    if finding.get("question"):
        result.append("**Вопрос для решения.** " + plain(finding["question"]))
    if options:
        for number, option in enumerate(options, 1):
            anchor = option["anchor"]
            if anchor not in evidence:
                raise ValueError("У предложения отсутствует проверенная цитата")
            text = (f'{number}. **Вариант {number}.** {cell(option["reading"])}\n\n'
                    f'   **Основание.** {refs([anchor["id"]])} «{plain(anchor["quote"])}».\n\n'
                    f'   **Ожидаемый результат.** {cell(option["effect"])}')
            if finding["kind"] == "Дефект":
                other_ids = [o["anchor"]["id"] for o in options if o["anchor"]["id"] != anchor["id"]]
                text += f'\n\n   При выборе этого варианта привести в соответствие {refs(other_ids)}.'
            result.append(text)
    elif finding.get("proposal_anchors"):
        # Ранее сохранённый объект содержит только буквальные основания без отдельных исходов.
        for number, anchor in enumerate(finding["proposal_anchors"], 1):
            if anchor not in evidence:
                raise ValueError("У предложения отсутствует проверенная цитата")
            result.append(f'{number}. Для трактовки {number} закрепить правило {refs([anchor["id"]])} '
                          f'«{plain(anchor["quote"])}». Указать условие применения этого варианта в критерии приёмки.')
    elif finding.get("reference"):
        result.append(f'Привести контракт и пример {refs(finding["ids"])} в соответствие с правилом '
                      f'«{plain(finding["reference"]["rule"])}». Проверяемое поведение — {plain(finding["scenario"])}')
        if not finding.get("test"):
            test = (f'Сверить исправленный контракт {refs(finding["ids"])} с внешним правилом '
                    f'«{plain(finding["reference"]["rule"])}». Проверить, что описанный эффект ему соответствует.')
    elif finding["fix"] and ("proposal_options" in finding or any(finding["fix"] == e["quote"] for e in evidence)):
        result.append(f'Проект правки по {refs(finding["ids"])} — {plain(finding["fix"])}')
        if not finding.get("test"):
            test = (f'Открыть исправленные пункты {refs(finding["ids"])} и проверить выполнение '
                    f'предложенной правки «{plain(finding["fix"])}».')
    else:
        result.append(f'Внести ответ на этот вопрос в {refs(finding["ids"])} для сценария «{plain(finding["scenario"])}».')
    result.append('**Черновик приёмочного теста.** ' + test)
    return result


def render(doc, result, run, source_path, output_path):
    blocks = {b.id: b for b in doc.blocks}
    try:
        rel = Path(os.path.relpath(source_path.resolve(), output_path.resolve().parent))
        source_link = quote(rel.as_posix(), safe="/.")
    except ValueError:  # На Windows у путей могут быть разные диски.
        source_link = source_path.resolve().as_uri()

    def source_location(block):
        if source_path.suffix.casefold() == ".docx":
            anchor = ""
        elif block.page:
            anchor = f"#page={block.page}"
        else:
            anchor = f"?plain=1#L{block.first_line}"
            if block.last_line != block.first_line:
                anchor += f"-L{block.last_line}"
        return f'[{plain(block.location)}]({source_link}{anchor})'

    def evidence(item):
        lines = plain(item["quote"]).splitlines()
        return f'{plain(item["section"])} · {source_location(blocks[item["block"]])}\n\n' + "\n".join(f"> {line}  " for line in lines)

    counts = result["counts"]
    findings = result["findings"]
    critical = [f for f in findings if f["counted"] and f["severity"] == "Критичная"]
    summary = result["set_review"]
    blocking_questions = [q for q in result['questions'] if q['blocking']]
    blockers = list(dict.fromkeys(ident for q in blocking_questions for ident in q['findings']))
    short_list = [f'{refs([ident])} {plain(f["topic"])}' for ident in blockers[:3]
                  for f in findings if f['id'] == ident]
    extra_rows = ''
    if run.get('settings'):
        cfg = run['settings']
        parameters = [f'{name}={cfg[name]}' for name in ('cli_version', 'temperature', 'seed', 'reasoning_effort', 'analysis_thinking_level', 'extract_workers')
                      if cfg.get(name) is not None]
        if cfg.get('temperature') is None and cfg.get('seed') is None:
            parameters.append('temperature и seed провайдер не сообщает')
        token_count = lambda key: str(run[key]) if run.get(key) is not None else 'не сообщено провайдером'
        extra_rows = (f'\n| Параметры запуска | {cell(", ".join(parameters))} |'
                      f'\n| Вызовов модели | {run["model_calls"]} |'
                      f'\n| Токены входа / выхода | {token_count("input_tokens")} / {token_count("output_tokens")} |'
                      f'\n| Метрики этапов | [run-meta.json]({quote(run["metrics_path"])}) |')
    parts = [
        f'# Статическое ревью · {plain(doc.title)}',
        f'**Проверено утверждений — {counts["requirements"]} · нарушений — {counts["defects"]} · '
        f'критичных дефектов — {len(critical)} · вопросов к автору — {counts["questions"]}.**',
        plain(summary["readiness"]),
        (f'**Блокирующих вопросов — {len(blocking_questions)}.** ' + ' · '.join(short_list)).rstrip(),
        "[Критичные дефекты](#critical) · [Вопросы и порядок согласования](#questions) · [Замечания](#findings) · "
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
        f'| Рабочая копия при старте | {run["state"]} |' + extra_rows,
        "## Проверка набора в целом", plain(summary["assessment"]),
        f'Открытых предполагаемых пробелов — {counts["gaps"]}. '
        f'Неоднозначностей — {counts["ambiguities"]}. Рекомендаций — {counts["recommendations"]}.',
        "Каждый ID утверждения учитывается один раз. В число нарушений входят подтверждённые дефекты "
        "и неоднозначности, для которых показаны две опирающиеся на текст трактовки с разными последствиями. "
        "Один и тот же конфликт имеет один ID при любом числе затронутых требований. "
        "Критичный дефект блокирует приёмку существенного обязательного сценария. Предполагаемый пробел "
        "оставляет открытым ожидаемое поведение или источник данных. Рекомендация предлагает улучшение. "
        "Вопросы и рекомендации имеют отдельные счётчики.",
        '<a id="critical"></a>\n\n## Критичные дефекты',
    ]
    parts.append("\n".join(f'- {refs([f["id"]])} · {plain(f["reason"])}' for f in critical)
                 or "Критичных дефектов не выявлено.")
    parts.append('<a id="questions"></a>\n\n## Вопросы к автору ТЗ')
    if result["questions"]:
        parts.append("Вопросы приведены в порядке согласования. Автор ТЗ фиксирует решение, "
                     "затем QA проверяет указанный сценарий.")
        by_id = {f["id"]: f for f in findings}
        contacts = _contacts(doc.blocks)
        used_contacts = {}
        stages = [[], [], [], []]
        for q in result["questions"]:
            ids = list(dict.fromkeys(q["findings"]))
            linked = [by_id[i] for i in ids]
            evidence_sections = {tuple(blocks[ev["block"]].section.split(" / "))
                                 for f in linked for ev in f["evidence"]}
            addresses = []
            for scope, block, label, value in contacts:
                if any(section[:len(scope)] == scope for section in evidence_sections):
                    target = f"contact-{block.id.lower()}"
                    used_contacts[target] = (scope, block, label, value)
                    addresses.append(f'[{plain(label)}](#{target})')
            prefix = "Блокирует приёмку" if q["blocking"] else "Требует уточнения"
            detail = f'{prefix} · {refs(ids)}. Зависимый сценарий — {plain(q["test"])}'
            if addresses:
                detail += "\n\nРоли в связанных разделах ТЗ — " + ", ".join(addresses) + "."
            stages[_question_stage(q, linked)].extend([f'**{plain(q["question"])}**', detail])
        if used_contacts:
            parts.append("### Кому передать вопросы")
            for target, (scope, block, label, value) in used_contacts.items():
                section = " / ".join(scope) or doc.title
                parts.append(f'<a id="{target}"></a>\n\n{plain(section)} · {plain(label)} — '
                             f'{plain(value)}. {source_location(block)}')
        headings = ("Согласовать до приёмки", "Выбрать исправление для выявленного нарушения",
                    "Уточнить ожидаемое поведение", "Разобрать детали низкого приоритета")
        for heading, entries in zip(headings, stages):
            if entries:
                parts.extend(["### " + heading, *entries])
    else:
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
        open_premise = f.get("open_premise")
        if f["scenario"]:
            parts.append(f'**Сценарий.** {plain(f["scenario"])}')
        if f["consequence"] and (not open_premise or f["consequence"] != open_premise["effect"]):
            parts.append(f'**Последствие.** {plain(f["consequence"])}')
        if open_premise:
            parts.append("**Что нужно уточнить.** " + plain(open_premise["condition"]))
            parts.append("**Как ответ изменит приёмку.** " + plain(open_premise["effect"]))
        parts.extend(question_basis(f))
        if f.get("shared_premise"):
            premise = f["shared_premise"]
            sources = ", ".join(f'{refs([a["id"]])} «{plain(a["quote"])}»' for a in premise["anchors"])
            parts.append(f'**Общее условие.** {plain(premise["condition"])} Основания — {sources}.')
        if f["interpretations"] and not f.get("proposal_options"):
            parts.append("\n".join(f'{i}. {plain(t)}' for i, t in enumerate(f["interpretations"], 1)))
        if f["fix"] and not f["counted"]:
            parts.append("**Исправление по тексту документа.** " + plain(f["fix"]))
        parts.extend(author_proposal(f))
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
        resolved_by = [ident for ident in dict.fromkeys(r.get("resolution_sources", [])) if ident != r["id"]]
        if resolved_by:
            parts.append("Основания для снятия замечания — " + refs(resolved_by) + ".")
    parts.extend(['<a id="decision"></a>\n\n## Готовность и порядок исправлений', plain(summary["readiness"])])
    if summary["priorities"]:
        finding_ids = {f["id"] for f in findings}
        def link_finding(match):
            ident = match.group()
            return refs([ident]) if ident in finding_ids else ident
        steps = [re.sub(r"\bZ-\d+\b", link_finding, plain(t)) for t in summary["priorities"]]
        parts.append("\n".join(f'{i}. {step}' for i, step in enumerate(steps, 1)))
    return "\n\n".join(parts) + "\n"
