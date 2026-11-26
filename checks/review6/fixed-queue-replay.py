"""Run the production adjudicator on all questions of the pinned preceding bank report."""
import argparse
from datetime import datetime
import hashlib
import html
import json
import os
from pathlib import Path
import re
import subprocess
import sys


OLD = "5669ac83c542c546e876765f397cccc2fe13ce9d"
OLD_REPORT = "7c7d666d065dabc8114b96db2791e6b90dffadd36316df44c73f0131fadaeb87"
SOURCE = "e7dae55e5453a250d93e335f5ff9c7f775f4457ccddd333f4a67e47b20d74381"
MODEL = "gpt-6.2-sol"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def literal(text):
    return html.unescape(re.sub(r"\\([\\`*_{}\[\]#|>~])", r"\1", text))


def field(body, label):
    match = re.search(r"^\*\*" + re.escape(label) + r"\.\*\* (.+)$", body, re.M)
    return literal(match[1]) if match else ""


def archive(repo):
    from requirements_validator.source import read_document
    from scripts.verify_report import verify

    path = repo / "reports/finish4/review.md"
    source = repo / "docs/requirements.md"
    meta = json.loads((path.with_suffix("") / "run-meta.json").read_bytes())
    assert meta["report_sha256"] == sha(path.read_bytes()) == OLD_REPORT
    assert meta["source_sha256"] == sha(source.read_bytes()) == SOURCE
    assert meta["commit"] == OLD and meta["model"] == MODEL and meta["working_tree"] == "чистая"
    counts = verify(path, source)
    doc = read_document(source)
    blocks = {b.id: b for b in doc.blocks}
    body = path.read_text("utf-8")
    sections = dict(re.findall(r'^<a id="([^"]+)"></a>\n(.*?)(?=^<a id="|\Z)', body, re.M | re.S))
    claims = {}
    for ident, entry in sections.items():
        if ident.startswith("r-"):
            ident = ident.upper()
            rows = re.findall(r"^> (.*)$", entry, re.M)
            quote = literal("\n".join(row.removesuffix("  ") for row in rows))
            block = blocks[ident.split("-")[1]]
            assert quote and quote in block.text
            claims[ident] = dict(id=ident, quote=quote, block=block.id, section=block.section)
    candidates = []
    pattern = r"^\*\*(.+?)\*\*\s*\n\s*\n(?:Блокирует приёмку|Требует уточнения) · (\[Z-\d+\]\([^)]*\))\. Зависимый сценарий — (.+)$"
    # Contact anchors break the section in this report. Read the whole question queue.
    segment = body.partition("## Вопросы к автору ТЗ\n")[2].partition('<a id="findings">')[0]
    for q, reference, test in re.findall(pattern, segment, re.M):
        ident = re.search(r"Z-\d+", reference)[0]
        entry = sections[ident.lower()]
        heading = re.search(r"^### " + ident + r" · (.+)$", entry, re.M)
        kind, category, severity, reason = re.search(r"^\*\*(.+?) · (.+?) · (.+?)\.\*\* (.*)$", entry, re.M).groups()
        direct = re.findall(r"\[(R-[\w-]+)\]", re.search("^Затронутые утверждения — (.+)$", entry, re.M)[1])
        evidence = []
        for ref, blockquote in re.findall(r"^\[(R-[\w-]+)\]\([^)]*\) · [^\n]+\n\n((?:> [^\n]*(?:\n|$))+)", entry, re.M):
            quote = literal("\n".join(line[2:].removesuffix("  ") for line in blockquote.splitlines()))
            assert quote and quote in claims[ref]["quote"]
            evidence.append(dict(claims[ref], quote=quote))
        assert set(direct) == {ev["id"] for ev in evidence}
        options = []
        readings = []
        for reading, ref, quote, effect in re.findall(r"^\d+\. \*\*Вариант \d+\.\*\* (.+)\n\n   \*\*Основание\.\*\* \[(R-[\w-]+)\]\([^)]*\) «(.+)»\.\n\n   \*\*Ожидаемый результат\.\*\* (.+)$", entry, re.M):
            reading, quote, effect = map(literal, (reading, quote, effect))
            anchor = next(ev for ev in evidence if ev["id"] == ref and ev["quote"] == quote)
            options.append(dict(reading=reading, effect=effect, anchor=anchor))
            readings.append(f"{reading} → {effect} ({ref}, «{quote}»)")
        external = re.search(r"^\*\*Внешнее основание\.\*\* (.+) \[(.+)\]\((.+)\)$", entry, re.M)
        ext = dict(zip(("rule", "title", "url"), map(literal, external.groups()))) if external else None
        consequence = field(entry, "Последствие") or field(entry, "Как ответ изменит приёмку")
        assert heading and reason and consequence and evidence and test
        if kind == "Неоднозначность" or kind == "Дефект" and category == "Противоречивость" and not ext:
            assert len(options) == 2, ident
        candidates.append(dict(id=ident, question=literal(q), test=literal(test), topic=literal(heading[1]),
                               scenario=field(entry, "Сценарий"), consequence=consequence,
                               reason=literal(reason), kind=kind, category=category, severity=severity,
                               counted=kind in {"Дефект", "Неоднозначность"}, ids=direct, evidence=evidence,
                               reference=ext, interpretations=readings, proposal_options=options,
                               fix=field(entry, "Исправление по тексту документа")))
    assert len(claims) == counts["requirements"] == 127
    assert len({f["id"] for f in candidates}) == len(candidates) == counts["questions"] == 17
    return doc, list(claims.values()), candidates


def prepare(doc, claims, candidates):
    from requirements_validator import engine as e
    blocks = doc.blocks
    payload = dict(blocks=[e._source(b) for b in blocks],
                   candidates=[e._audit_candidate(f) for f in candidates],
                   claims=[{k: c[k] for k in ("id", "block", "quote")} for c in claims])
    # A published report contains no intermediate traces from the previous synthesis.
    # Omit trace_review rather than passing fabricated traces or author decisions.
    signals = e.source_signals(blocks, claims)
    measurements = e.observation_scope.measurement_scopes(blocks, claims)
    unbound = e.unbound_response_examples(blocks)
    capacities = e.capacity_pairs(blocks, claims)
    scheduled = e.command_rules.scheduled_command_pairs(claims)
    instructions = e.ADJUDICATE
    for key, data, text in (
        ("source_signals", signals, e.SIGNAL_INSTRUCTION),
        ("named_transition_targets", e.named_transition_targets(claims), e.TRANSITION_INSTRUCTION),
        ("refund_rules", e.refund_rules(claims), e.REFUND_INSTRUCTION),
        ("returned_state_on_error", e.response_obligations(blocks), e.REPRESENTATION_INSTRUCTION),
        ("measurement_scopes", measurements, e.observation_scope.INSTRUCTION),
        ("response_examples_without_request", unbound, e.EXAMPLE_SCOPE_INSTRUCTION),
        ("capacity_pairs", capacities, e.CAPACITY_INSTRUCTION),
        ("scheduled_command_rules", scheduled, e.command_rules.INSTRUCTION),
    ):
        if data:
            payload[key] = data
            instructions += "\n" + text
    boundaries = e.source_boundaries(blocks)
    scopes = e.candidate_scopes(candidates)
    if boundaries or scopes or e.identifier_limits(blocks):
        instructions += "\n" + e.SCOPE_INSTRUCTION
    if boundaries:
        payload["source_boundaries"] = boundaries
    if scopes:
        payload["question_scopes"] = scopes
    # Production would add the reference-specific instruction only if a missing target had been verified.
    assert not e.missing_references(blocks)
    assert payload.get("refund_rules") and payload.get("returned_state_on_error")
    def adjudicate(data):
        kept, _, _ = e._final_decisions(data, candidates, claims, signals, (), capacities, unbound, scheduled, measurements)
        return kept, e._questions(kept)
    return instructions, payload, adjudicate


def save(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def now():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def run(options, commit, doc, claims, candidates, prepared):
    from requirements_validator import engine as e
    from requirements_validator.metrics import RunMetrics, stage
    from requirements_validator.provider import get_provider
    from requirements_validator.report import plain
    output = options.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    record = output / "fixed-queue.json"
    if record.exists():
        raise ValueError("Полный результат уже существует")
    provider = get_provider()
    assert provider.model == MODEL and provider.name == "OpenAI через Codex CLI"
    instructions, payload, verify = prepared
    attempts = output / "fixed-queue-attempts"
    attempts.mkdir(exist_ok=True)
    applied = {}
    for i in range(1, 4):
        dest = attempts / f"attempt-{i}.json"
        if dest.exists():
            previous = json.loads(dest.read_bytes())
            assert previous["implementation"] == commit and previous["status"] == "отклонён", dest
            continue
        metrics = RunMetrics()
        receipt = dict(implementation=commit, started=now(), status="запущен", diagnostics=[], responses=[])
        def ask(prompt, schema):
            recording = dict(prompt_sha256=sha(prompt.encode()), schema_sha256=sha(e.compact(schema).encode()))
            receipt["responses"].append(recording)
            result = provider.ask(prompt, schema)
            recording["response"] = result
            return result
        class Traced:
            pass
        transport = Traced()
        transport.ask = ask
        def diagnose(message):
            print(message, flush=True)
            receipt["diagnostics"].append(message)
        print("Попытка", i, "·", receipt["started"], flush=True)
        try:
            with metrics.capture():
                stage("adjudication")
                kept, questions = e._request(transport, instructions, payload, e.AUDIT, verify, diagnose)
        except ValueError as err:
            receipt.update(status="отклонён", error=str(err), finished=now(), metrics=metrics.summary())
            save(dest, receipt)
            print(receipt["error"], flush=True)
            if not str(err).startswith(("Повторный ответ модели не прошёл проверку", "Модель вернула некорректный JSON",
                                         "Истёк таймаут", "Повторные правки", "Codex CLI завершился с кодом")):
                raise
            continue
        receipt.update(status="принят", finished=now(), metrics=metrics.summary())
        save(dest, receipt)
        applied = {f["id"]: f for f in kept}
        break
    else:
        raise ValueError("Исчерпаны три технические попытки, результаты сохранены")
    grouped = {ident: row for row in questions for ident in row["findings"]}
    rows = []
    for f in candidates:
        ident = f["id"]
        current = applied.get(ident, {})
        group = grouped.get(ident)
        independent = bool(group and group["findings"] == [ident])
        rows.append(dict(id=ident, retained_independently=independent, question=current.get("question",""),
                         test=current.get("test",""), source_ids=current.get("ids", []),
                         basis=current.get("question_basis", {}), related=group["findings"] if group else []))
    result = dict(implementation=commit, mode="отдельная рецензия фиксированной очереди", provider=provider.name,
                  generation=provider.configuration(), model=provider.model, source_sha256=SOURCE,
                  input_report_sha256=OLD_REPORT, input_implementation=OLD, block_count=len(doc.blocks),
                  claim_count=len(claims), input_questions=len(candidates), output_questions=len(questions),
                  independently_retained=sum(r["retained_independently"] for r in rows), attempts=i,
                  instruction_sha256=sha(instructions.encode()), payload_sha256=sha(e.compact(payload).encode()),
                  payload_fields=list(payload), named_transition_targets=payload.get("named_transition_targets", []),
                  results=rows)
    save(record, result)
    lines = ["# Повторная рецензия 17 исходных вопросов", "",
             f"На `{commit[:7]}` модель `{MODEL}` получила все 17 ранее опубликованных карточек одним запросом, "
             "вместе со 127 исходными утверждениями и полным текстом ТЗ. Материалы взяты из "
             "[предыдущего отчёта](../../reports/finish4/review.md). Извлечение и сквозной поиск кандидатов "
             "в этом эксперименте не выполнялись. Предыдущий отчёт не содержит внутренней трассировки этапа синтеза. "
             "Рецензия использовала опубликованные формулировки, цитаты, варианты и связи карточек. "
             "В модели отсутствовали редакторские ответы к этим карточкам.", "",
             f"Сохранено самостоятельных вопросов {result['independently_retained']} из {len(rows)}. "
             "Этот счётчик проверяет присутствие каждого вопроса, смысловая оценка выполняется отдельно. "
             f"Принята первая технически успешная рецензия, попытка {i}. "
             "[Данные результата](fixed-queue.json) · " + " · ".join(
                 f"[Попытка {n}](fixed-queue-attempts/attempt-{n}.json)" for n in range(1,i+1)), ""]
    for row in rows:
        ident = row["id"]
        lines += [f"## {ident}", "", f"[Исходная карточка](../../reports/finish4/review.md#{ident.lower()})", ""]
        if row["question"]:
            lines += ["**" + plain(row["question"]) + "**", "", plain(row["test"]), ""]
        if not row["retained_independently"]:
            lines += ["Карточка снята либо объединена с другой. Самостоятельный вопрос не зачтён.", ""]
        if row["basis"]:
            lines += ["Исходы проверки по ответу автора — " + " / ".join(plain(x) for x in row["basis"]["outcomes"]), ""]
    (output/"fixed-queue.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: result[k] for k in ("model", "attempts", "input_questions", "output_questions", "independently_retained")},
                     ensure_ascii=False), flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--clone", type=Path, default=Path.cwd())
    p.add_argument("--commit", required=True)
    p.add_argument("--output", type=Path)
    opt = p.parse_args()
    repo = opt.clone.resolve()
    git = lambda *args: subprocess.check_output(["git", *args], cwd=repo, text=True).strip()
    assert git("rev-parse", "HEAD") == opt.commit and not git("status","--porcelain")
    if opt.output:
        opt.output = opt.output.resolve()
        assert not opt.output.is_relative_to(repo), "Клон запуска должен сохранять чистоту."
    os.chdir(repo)
    sys.path.insert(0, str(repo))
    from requirements_validator import engine
    assert Path(engine.__file__).resolve().is_relative_to(repo)
    doc, claims, candidates = archive(repo)
    prepared = prepare(doc, claims, candidates)
    print(f"Проверены {len(claims)} утверждений, {len(doc.blocks)} блоков и {len(candidates)} карточек. SHA проверены.", flush=True)
    if opt.output:
        run(opt, opt.commit, doc, claims, candidates, prepared)
    assert not git("status", "--porcelain")


if __name__ == "__main__":
    if not __debug__:
        raise SystemExit("Запускайте без параметра -O.")
    main()
