"""Заслеплённая оценка отчётов по размеченному корпусу Markdown."""

import argparse
import hashlib
import itertools
import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.parse import quote, unquote

from requirements_validator.__main__ import save_complete
from requirements_validator.report import cell


ROOT = Path(__file__).resolve().parents[1]
KINDS = ("Дефект", "Неоднозначность", "Предполагаемый пробел", "Рекомендация")


@dataclass(frozen=True)
class Seed:
    id: str
    type: str
    category: str
    ranges: tuple
    description: str


@dataclass(frozen=True)
class Case:
    id: str
    split: str
    path: Path
    seeds: tuple
    sha: str
    lines: int


@dataclass(frozen=True)
class Finding:
    id: str
    kind: str
    category: str
    title: str
    lines: frozenset


@dataclass(frozen=True)
class Report:
    path: Path
    commit: str
    provider: str
    started: str
    findings: tuple
    configuration: str = ""
    clean: bool = False


def load_cases(root, split):
    cases = []
    identifiers = set()
    for manifest in sorted(root.glob("*/manifest.json")):
        data = json.loads(manifest.read_text(encoding="utf-8"))
        if split != "all" and data["split"] != split:
            continue
        ident = data["id"]
        if ident != manifest.parent.name or not re.fullmatch(r"[a-z][a-z0-9-]+", ident):
            raise ValueError(f"Некорректный ID документа в {manifest.name}")
        for field in ("source", "baseline"):
            if field not in data:
                continue
            path = manifest.parent / data[field]
            if path.resolve().parent != manifest.parent.resolve():
                raise ValueError("Путь ТЗ должен быть внутри каталога манифеста")
            content = path.read_bytes()
            lines = len(content.decode("utf-8-sig").splitlines())
            seeds = []
            for entry in data["seeds"] if field == "source" else []:
                ranges = tuple(tuple(pair) for pair in entry["ranges"])
                if not ranges or any(not 1 <= lo <= hi <= lines for lo, hi in ranges):
                    raise ValueError(f"Некорректный диапазон {entry['id']} в {path.name}")
                if entry["id"] in identifiers:
                    raise ValueError(f"Повтор ID дефекта {entry['id']}")
                identifiers.add(entry["id"])
                seeds.append(Seed(entry["id"], entry["type"], entry["category"], ranges, entry["description"]))
            case_id = ident if field == "source" else ident + "-base"
            cases.append(Case(case_id, data["split"], path, tuple(seeds), hashlib.sha256(content).hexdigest(), lines))
    if not cases or len({c.id for c in cases}) != len(cases):
        raise ValueError("В выбранной части корпуса нет документов или пересекаются ID")
    return cases


def parse_report(path, case):
    body = path.read_text(encoding="utf-8")

    def field(label):
        match = re.search(r"^\| " + re.escape(label) + r" \| (.+?) \|$", body, re.M)
        if not match:
            raise ValueError(f"{case.id}: отсутствует поле паспорта «{label}»")
        return match[1].strip("`")

    if field("SHA-256 исходных байтов") != case.sha:
        raise ValueError(f"{case.id}: SHA-256 входа в паспорте не совпадает с манифестом")
    if '<a id="decision"></a>' not in body or '<a id="findings"></a>' not in body:
        raise ValueError(f"{case.id}: неполный отчёт")
    commit = field("Коммит реализации")
    if not re.fullmatch(r"[\da-f]{40}", commit):
        raise ValueError(f"{case.id}: паспорт не содержит хэш коммита")
    provider = field("Провайдер и модель").replace("`", "")
    started = field("Начало / окончание").split(" / ")[0]
    datetime.fromisoformat(started)
    findings = []
    for heading in re.finditer(r'^### (Z-\d+) · (.+?)\n\n\*\*([^*·]+) · ([^*·]+) · ([^*\n]+)\.\*\*', body, re.M):
        ident, title, kind, category, _ = heading.groups()
        if kind not in KINDS:
            raise ValueError(f"{case.id}: неизвестный вид замечания {kind}")
        end = body.find('\n<a id="', heading.end())
        section = body[heading.end():end if end >= 0 else len(body)]
        lines = set()
        for match in re.finditer(r'^\[R-[^\n]+? · \[строк[аи] (\d+)(?:–(\d+))?\]\([^\n]*?#L(\d+)\)\s*\n\s*\n>', section, re.M):
            lo, hi, anchor = int(match[1]), int(match[2] or match[1]), int(match[3])
            if lo != anchor or not 1 <= lo <= hi <= case.lines:
                raise ValueError(f"{case.id}/{ident}: недопустимая ссылка на строки {lo}–{hi}")
            lines.update(range(lo, hi + 1))
        if not lines:
            raise ValueError(f"{case.id}/{ident}: нет адресованных цитат")
        findings.append(Finding(ident, kind, category, title, frozenset(lines)))
    anchors = re.findall(r'^<a id="(z-\d+)"></a>$', body, re.M)
    if sorted(x.id.lower() for x in findings) != sorted(anchors) or len(set(anchors)) != len(anchors):
        raise ValueError(f"{case.id}: реестр и карточки замечаний расходятся")
    meta_file = path.parent / path.stem / "run-meta.json"
    config = ""
    clean = False
    if meta_file.is_file():
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if (meta["report_sha256"], meta["source_sha256"], meta["commit"], meta["started_at"]) != (
                digest, case.sha, commit, started):
            raise ValueError(f"{case.id}: run-meta.json относится к другому отчёту")
        if provider != f"{meta['provider']} · {meta['model']}":
            raise ValueError(f"{case.id}: модель в паспорте и метриках различается")
        if meta["working_tree"] != field("Рабочая копия при старте"):
            raise ValueError(f"{case.id}: статус рабочей копии в метриках и отчёте различается")
        clean = meta["working_tree"] == "чистая"
        config = json.dumps(meta["generation"], sort_keys=True, ensure_ascii=False)
    return Report(path, commit, provider, started, tuple(findings), config, clean)


def match_seeds(seeds, findings):
    """Зачесть только взаимно однозначную пару по всем заявленным местам и категории."""
    candidates = defaultdict(list)
    competitors = defaultdict(list)
    partial = defaultdict(list)
    for seed in seeds:
        for finding in findings:
            hit = [any(lo <= line <= hi for line in finding.lines) for lo, hi in seed.ranges]
            if all(hit) and seed.category == finding.category:
                candidates[seed.id].append(finding.id)
                competitors[finding.id].append(seed.id)
            elif any(hit):
                partial[finding.id].append(seed.id)
    matches = {sid: ids[0] for sid, ids in candidates.items()
               if len(ids) == 1 and len(competitors[ids[0]]) == 1}
    manual = {}
    for finding in findings:
        if finding.id in matches.values():
            continue
        nearby = competitors[finding.id] + partial[finding.id]
        manual[finding.id] = (", ".join(sorted(set(nearby))) if nearby
                              else "Вне эталонных диапазонов")
    return matches, manual


def stability(reports):
    """Сравнить находки без знания разметки. Спорные слияния не повышают стабильность."""
    records = {(i, finding.id): finding for i, report in enumerate(reports, 1) for finding in report.findings}
    edges = {key: set() for key in records}
    for a, b in itertools.combinations(records, 2):
        fa, fb = records[a], records[b]
        if a[0] != b[0] and fa.category == fb.category and fa.lines & fb.lines:
            edges[a].add(b)
            edges[b].add(a)
    groups = []
    todo = set(records)
    while todo:
        first = min(todo)
        component, pending = set(), [first]
        while pending:
            item = pending.pop()
            if item not in component:
                component.add(item)
                pending.extend(edges[item] - component)
        todo -= component
        common = set.intersection(*(set(records[k].lines) for k in component))
        ambiguous = len({r for r, _ in component}) != len(component) or not common
        if ambiguous:
            groups.extend(([k], True) for k in sorted(component))
        else:
            groups.append((sorted(component), False))
    return groups


def report_path(directory, case, repeat):
    return directory / case.id / f"r{repeat}" / "report.md"


def check_layout(cases, directory, published):
    for case in cases:
        scratch = report_path(directory, case, 1)
        final = report_path(published, case, 1)
        if os.path.relpath(case.path, scratch.parent) != os.path.relpath(case.path, final.parent):
            raise ValueError("Относительные ссылки на исходник в --runs-dir и итоговой папке различаются. "
                             "Используйте .tmp/benchmark-runs с reports/evaluation.md или укажите "
                             "две папки равной глубины внутри репозитория.")


def check_official(report, case):
    if not report.configuration or not report.clean:
        raise ValueError(f"{case.id}: для официальной оценки нужны run-meta.json и чистая рабочая копия при старте")
    body = report.path.read_text(encoding="utf-8")
    match = re.search(r"^\| Входной файл \| \[[^\n]*?\]\(([^)]+)\) \|$", body, re.M)
    target = (report.path.parent / unquote(match[1])).resolve() if match else None
    if not target or not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest() != case.sha:
        raise ValueError(f"{case.id}: ссылка из отчёта не ведёт на исходный документ корпуса")


def generate(case, repeat, directory, resume, head, desired, jobs):
    path = report_path(directory, case, repeat)
    if resume and path.is_file():
        cached = parse_report(path, case)
        check_official(cached, case)
        if cached.commit != head or not cached.configuration:
            raise ValueError(f"{case.id}/r{repeat}: другой коммит или отсутствуют метрики. Задайте новый --runs-dir")
        observed = json.loads(cached.configuration)
        if not cached.provider.startswith(desired[0] + " · ") or any(
                value != observed.get(key) for key, value in desired[1].items() if key != "model_version_reported"):
            raise ValueError(f"{case.id}/r{repeat}: изменилась конфигурация модели. Задайте новый --runs-dir")
        return
    # Проверяющая модель видит только входной документ. Манифест обрабатывает оценщик.
    path.parent.mkdir(parents=True, exist_ok=True)
    print(f"{case.id} · прогон {repeat}", flush=True)
    command = [sys.executable, "-m", "requirements_validator", "--input", str(case.path.relative_to(ROOT)),
               "--output", os.path.relpath(path, ROOT)]
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    if jobs > 1:
        env["CODEX_EXTRACT_WORKERS"] = "1"
    proc = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, encoding="utf-8", errors="replace")
    if proc.returncode:
        diagnostic = (proc.stderr.strip() or proc.stdout.strip()).splitlines()
        raise ValueError(f"{case.id}/r{repeat}: CLI вернул {proc.returncode}. "
                         + (diagnostic[-1] if diagnostic else "Нет диагностики"))
    result = parse_report(path, case)
    check_official(result, case)
    if result.commit != head:
        raise ValueError(f"{case.id}/r{repeat}: версия кода изменилась во время запуска")
    print(f"{case.id} · прогон {repeat} сохранён", flush=True)


def ratio(numerator, denominator):
    return (f"{numerator}/{denominator} ({100 * numerator / denominator:.1f}%)"
            if denominator else "— (знаменатель 0)")


def link(path, output, label, anchor=""):
    relative = Path(os.path.relpath(path, output.parent)).as_posix()
    return f"[{label}]({quote(relative, safe='/.-')}{anchor})"


def evaluate(cases, report_sets, output):
    providers, commits, configs = set(), set(), set()
    by_case, review_rows, stability_rows, seed_rows = [], [], [], []
    stats, by_type = defaultdict(Counter), defaultdict(Counter)
    repeats = len(report_sets[cases[0].id])
    for case in cases:
        reports = report_sets[case.id]
        if len(reports) != repeats or len({r.started for r in reports}) != repeats:
            raise ValueError(f"{case.id}: повторы должны происходить из разных запусков")
        matches_by_run = []
        for idx, report in enumerate(reports, 1):
            providers.add(report.provider)
            commits.add(report.commit)
            configs.add(report.configuration)
            matches, manual = match_seeds(case.seeds, report.findings)
            matches_by_run.append(matches)
            total = len(report.findings)
            count = len(matches)
            for name in (case.split, "all"):
                stats[(name, idx)].update(found=count, seeded=len(case.seeds), reported=total)
            for seed in case.seeds:
                by_type[(seed.type, idx)].update(found=int(seed.id in matches), seeded=1)
            ref = link(report.path, output, f"{case.id} · {idx}")
            by_case.append(f"| {ref} | {case.split} | {len(case.seeds)} | {total} | {count} |")
            for finding in report.findings:
                if finding.id in manual:
                    review_rows.append(f"| {ref} | {finding.id} | {cell(finding.title)} | {cell(finding.category)} "
                                       f"| {', '.join(map(str, sorted(finding.lines)))} | {manual[finding.id]} |")
        for seed in case.seeds:
            ranges = ", ".join(str(a) if a == b else f"{a}–{b}" for a, b in seed.ranges)
            statuses = []
            for i, matches in enumerate(matches_by_run):
                fid = matches.get(seed.id)
                statuses.append(link(reports[i].path, output, fid, "#" + fid.lower()) if fid else "пропуск")
            seed_rows.append(f"| {case.id} / {case.split} | {seed.id} | {cell(seed.type)} | {cell(seed.category)} "
                             f"| {ranges} | {cell(seed.description)} | " + " · ".join(statuses) + " |")
        for group, uncertain in stability(reports):
            row_refs = []
            for idx, fid in group:
                row_refs.append(link(reports[idx-1].path, output, f"{idx}/{fid}", "#" + fid.lower()))
            first, fid = group[0]
            original = next(f for f in reports[first-1].findings if f.id == fid)
            marker = " · спорное соответствие" if uncertain else ""
            stability_rows.append((len(group), not uncertain,
                f"| {case.id} | {cell(original.title)} | {cell(original.category)} | {len(group)}/{repeats}{marker} "
                f"| {', '.join(row_refs)} |"))
    if len(providers) != 1 or len(commits) != 1 or len(configs) != 1:
        raise ValueError("Отчёты корпуса используют разные модели, параметры генерации или коммиты")
    manual_path = output.with_name(output.stem + "-manual.md")
    manual_header = ["# Случаи для независимой проверки", "",
        "Эти замечания не получили автоматического балла. Человек может проверить смысл находки по исходному отчёту. "
        "На контрольных документах такие замечания представляют кандидатов в ложные срабатывания.", "",
        "| Отчёт | ID | Замечание | Категория | Строки | Возможные эталоны |", "|---|---|---|---|---|---|"]
    manual_text = "\n".join(manual_header + review_rows + ([] if review_rows else ["", "Спорных и незачтённых замечаний нет."])) + "\n"
    overall = stats["all", 1]
    stable = sum(n == repeats and certain for n, certain, _ in stability_rows)
    lines = ["# Качество на размеченном корпусе", "",
        f"Дата оценки {datetime.now().astimezone().isoformat(timespec='seconds')}. "
        f"Провайдер и модель — {next(iter(providers))}. Коммит реализации — `{next(iter(commits))}`.",
        "", "Основной результат измерен по первому запуску каждого документа. "
        f"Полнота — **{ratio(overall['found'], overall['seeded'])}**. "
        f"Точность — **{ratio(overall['found'], overall['reported'])}**."]
    if repeats > 1:
        lines.extend(["", f"Во всех {repeats} прогонах воспроизвелось **{ratio(stable, len(stability_rows))}** групп замечаний."])
    if not all(r.clean and r.configuration for series in report_sets.values() for r in series):
        lines.extend(["", "**Диагностический импорт.** Среди исходных отчётов есть версии без отдельных метрик "
                      "run-meta.json или без подтверждённой чистой рабочей копии."])
    lines += ["", "## Метод", "", "Разметка и базовые версии не включаются в запросы модели. Балл даётся "
        "за точную категорию и пересечение цитат со всеми раздельно заданными диапазонами дефекта. "
        "Только одна пара «замечание — дефект» может получить балл. Конкурирующие пары и совпадения "
        "лишь по строкам остаются незачтёнными. Требования к совпадению зафиксированы до измерения. "
        "В знаменатель точности входят все опубликованные карточки Z, включая вопросы и рекомендации. "
        "Существование других реальных дефектов, включая контрольные документы, возможно. "
        + link(manual_path, output, "Незачтённые замечания для проверки человеком"), "",
        "Результаты dev и test приведены отдельно. Dev служит для разработки. Разметка test предназначена "
        "для измерения после фиксации механизма и не должна применяться для подбора подсказок.", "",
        "| Часть | Прогон | Полнота | Точность |", "|---|---:|---:|---:|"]
    for (split, i), s in sorted(stats.items()):
        lines.append(f"| {split} | {i} | {ratio(s['found'],s['seeded'])} | {ratio(s['found'],s['reported'])} |")
    lines += ["", "## Типы дефектов", "", "| Тип | Прогон | Найдено / заложено |", "|---|---:|---:|"]
    lines += [f"| {cell(label)} | {i} | {ratio(s['found'],s['seeded'])} |" for (label,i),s in sorted(by_type.items())]
    lines += ["", "## Каждый эталон", "", "| ТЗ / часть | ID | Тип | Категория | Строки | Дефект | Прогоны по порядку |",
              "|---|---|---|---|---|---|---|", *seed_rows, "", "## Сохранённые отчёты и контрольные документы", "",
              "| Отчёт и прогон | Часть | Заложено | Замечаний | Зачтено |", "|---|---|---:|---:|---:|", *by_case,
              "", "## Воспроизводимость замечаний", "",
              "В одном документе сравниваются независимо полученные находки одной категории, у которых есть общая "
              "строка доказательства во всех вошедших прогонах и не более одного замечания в каждом. "
              "Конкурирующие или транзитивные совпадения показаны по отдельности и не дают балла устойчивости.",
              "", "| ТЗ | Замечание | Категория | Частота | Прогон и ID |", "|---|---|---|---:|---|",
              *(s for _, _, s in stability_rows)]
    return "\n".join(lines) + "\n", manual_path, manual_text


def stability_only(paths, output, source):
    first_path = paths[0].resolve()
    if source is None:
        first = first_path.read_text(encoding="utf-8")
        match = re.search(r"^\| Входной файл \| \[[^\n]*?\]\(([^)]+)\) \|$", first, re.M)
        if not match:
            raise ValueError("Передайте путь к исходному Markdown через --source")
        source = first_path.parent / unquote(match[1])
    data = source.read_bytes()
    count = len(data.decode("utf-8-sig").splitlines())
    case = Case(source.name, "", source, (), hashlib.sha256(data).hexdigest(), count)
    if output in {source.resolve(), *(p.resolve() for p in paths)}:
        raise ValueError("Для результата сравнения укажите отдельный выходной Markdown")
    reports = [parse_report(p.resolve(), case) for p in paths]
    if (len({(r.provider, r.commit, r.configuration) for r in reports}) != 1
            or len({r.started for r in reports}) != len(reports)):
        raise ValueError("Нужны три различных запуска одной модели и одной версии на одном документе")
    rows = []
    groups = stability(reports)
    for mentions, ambiguous in groups:
        first_run, fid = mentions[0]
        f = next(f for f in reports[first_run - 1].findings if f.id == fid)
        found = {i: link(reports[i-1].path, output, ident, "#" + ident.lower()) for i, ident in mentions}
        frequency = f"{len(mentions)}/3" + (" · нужна ручная сверка" if ambiguous else "")
        rows.append(f"| {cell(f.title)} | {cell(f.category)} | {frequency} | "
                    + " | ".join(found.get(i, "—") for i in (1, 2, 3)) + " |")
    stable = sum(len(g) == 3 and not ambiguous for g, ambiguous in groups)
    text = ["# Стабильность ревью на одном документе", "",
        f"Воспроизвелось во всех трёх независимых запусках **{ratio(stable, len(groups))}** групп замечаний.", "",
        f"Документ — {link(source, output, source.name)}. SHA-256 — `{case.sha}`. "
        f"Провайдер и модель — {reports[0].provider}. Версия — `{reports[0].commit}`.", "",
        "Совпадение требует одинаковой категории и общей строки цитаты. Если несколько находок одного "
        "запуска претендуют на одно соответствие или у цепочки совпадений нет общей строки, каждая такая "
        "находка остаётся отдельным упоминанием для ручной проверки и не добавляется в числитель.", "",
        "| Замечание | Категория | Частота | Прогон 1 | Прогон 2 | Прогон 3 |", "|---|---|---|---|---|---|", *rows]
    save_complete(output, "\n".join(text) + "\n")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeat", type=int, choices=range(1, 11), default=3)
    parser.add_argument("--split", choices=("all", "dev", "test"), default="all")
    parser.add_argument("--jobs", type=int, choices=(1, 2), default=1)
    parser.add_argument("--runs-dir", type=Path, default=ROOT / ".tmp" / "benchmark-runs")
    parser.add_argument("--import-dir", type=Path, help="считать существующие <case>/r1/report.md без вызовов модели")
    parser.add_argument("--stability-only", type=Path, nargs=3, metavar=("R1", "R2", "R3"),
                        help="сравнить три реальных отчёта об одном Markdown без эталонной разметки")
    parser.add_argument("--source", type=Path, help="явный исходный файл для --stability-only")
    parser.add_argument("--resume", action="store_true", help="использовать успешные прогоны той же версии")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    default_name = "stability.md" if args.stability_only else "evaluation.md"
    output = (args.output or ROOT / "reports" / default_name).resolve()
    try:
        if output.suffix.lower() != ".md":
            raise ValueError("Файл результата должен иметь расширение .md")
        if args.stability_only:
            stability_only(args.stability_only, output, args.source)
            print(f"Проверка стабильности сохранена: {output.name}.")
            return 0
        cases = load_cases(ROOT / "benchmark", args.split)
        directory = (args.import_dir or args.runs_dir).resolve()
        published = output.parent / "benchmark-runs"
        if not args.import_dir:
            check_layout(cases, directory, published)
            status = subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip()
            if status:
                raise ValueError("Для запуска используйте чистый клон реализации. Временные результаты "
                                 "хранятся в игнорируемом каталоге .tmp/benchmark-runs.")
            from requirements_validator.provider import get_provider
            provider = get_provider()
            config = provider.configuration()
            if args.jobs > 1:
                if provider.name == "Gemini API":
                    raise ValueError("Для Gemini укажите --jobs 1, чтобы соблюдать общую частоту запросов")
                config["extract_workers"] = 1
            head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
            with ThreadPoolExecutor(max_workers=args.jobs) as pool:
                queue = [pool.submit(generate, c, i, directory, args.resume, head, (provider.name, config), args.jobs)
                         for i in range(1, args.repeat+1) for c in cases]
                try:
                    for future in as_completed(queue):
                        future.result()
                except BaseException:
                    for future in queue:
                        future.cancel()
                    raise
        results = {c.id: [parse_report(report_path(directory, c, i), c) for i in range(1, args.repeat+1)] for c in cases}
        if output in {c.path.resolve() for c in cases} | {r.path for values in results.values() for r in values}:
            raise ValueError("Нельзя перезаписывать входной документ или отчёт эксперимента")
        # Сначала валидируем весь набор; прежняя оценка переживает любой прерванный запуск.
        summary, manual, review = evaluate(cases, results, output)
        if args.import_dir:
            for c in cases:
                for r in results[c.id]:
                    if r.configuration and r.clean:
                        check_official(r, c)
            save_complete(manual, review)
            save_complete(output, summary)
            print(f"Оценка пересчитана: {output.name}. Случаи для проверки: {manual.name}.")
            return 0
        for c in cases:
            for i, r in enumerate(results[c.id], 1):
                target = report_path(published, c, i)
                if r.path != target:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(r.path, target)
                    meta = r.path.parent / r.path.stem / "run-meta.json"
                    if meta.is_file():
                        destination = target.parent / target.stem / "run-meta.json"
                        destination.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(meta, destination)
                final_report = parse_report(target, c)
                check_official(final_report, c)
                results[c.id][i-1] = final_report
        summary, manual, review = evaluate(cases, results, output)
        save_complete(manual, review)
        save_complete(output, summary)
        print(f"Оценка сохранена: {output.name}. Случаи для проверки: {manual.name}.")
        return 0
    except (ValueError, KeyError, OSError, subprocess.SubprocessError) as exc:
        print(f"Ошибка оценки. {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
