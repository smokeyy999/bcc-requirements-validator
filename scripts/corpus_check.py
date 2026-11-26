"""Run the public CLI on five independent inputs, or rebuild the table from stored runs."""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

from requirements_validator.__main__ import save_complete
from requirements_validator.provider import _read_settings


ROOT = Path(__file__).resolve().parents[1]
CASES = {
    "archive_handover": ("archive_handover.md", "Длинное ТЗ архивного журнала"),
    "radio_schedule": ("radio_schedule.md", "Английское ТЗ с таблицей"),
    "map_sample": ("map_sample.pdf", "Одностраничная спецификация в PDF"),
    "balance_comparison": ("balance_comparison.md", "Финансовый контроль без внесённых дефектов"),
    "truncated": ("truncated.pdf", "Повреждённый PDF"),
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verified_measurement(folder, name, corpus):
    path = folder / name / "measurement.json"
    if not path.is_file():
        return None
    row = json.loads(path.read_text(encoding="utf-8"))
    src = corpus / "inputs" / CASES[name][0]
    if row["source_sha256"] != digest(src):
        return None
    for filename, sha in row["files_sha256"].items():
        asset = path.parent / filename
        if not asset.is_file() or digest(asset) != sha:
            return None
    return row


def run_case(name, folder, resume, commit, config, checkout):
    corpus = checkout / "checks/corpus"
    prior = verified_measurement(folder, name, corpus) if resume else None
    if prior and prior["outcome"] != "сбой" and prior["commit"] == commit and prior["configuration"] == config:
        print(f"{name}: использован ранее проверенный результат.", flush=True)
        return True
    source = corpus / "inputs" / CASES[name][0]
    dest = folder / name
    dest.mkdir(parents=True, exist_ok=True)
    report = dest / "report.md"
    meta = dest / "report/run-meta.json"
    args = ["-m", "requirements_validator", "--input", os.path.relpath(source, checkout).replace(os.sep, "/"),
            "--output", os.path.relpath(report, checkout).replace(os.sep, "/")]
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8", PYTHONUNBUFFERED="1")
    started = datetime.now().astimezone().isoformat(timespec="seconds")
    start = time.perf_counter()
    print(f"{name}: запущен CLI.", flush=True)
    with subprocess.Popen([sys.executable, *args], cwd=checkout, env=env, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace") as process:
        transcript = []
        for line in process.stdout:
            transcript.append(line)
            print(f"{name}: {line.rstrip()}", flush=True)
        code = process.wait()
    elapsed = round(time.perf_counter() - start, 3)
    console = "".join(transcript)
    log = dest / "stdout.txt"
    save_complete(log, console)
    files = {"stdout.txt": digest(log)}
    result = dict(started_at=started, command=["python", *args], exit_code=code, elapsed_seconds=elapsed,
                  source=source.name, source_bytes=source.stat().st_size, source_sha256=digest(source),
                  commit=commit, configuration=config, files_sha256=files, counts=None, diagnostic="")
    if not code and name != "truncated" and report.is_file() and meta.is_file():
        data = json.loads(meta.read_text(encoding="utf-8"))
        if (data["source_sha256"], data["commit"], data["report_sha256"]) != (digest(source), commit, digest(report)):
            raise ValueError(f"{name}: паспорт отличается от входа, результата или коммита кода.")
        result.update(outcome="отчёт", counts=data["counts"], model=data["model"], working_tree=data["working_tree"])
        files.update({"report.md": digest(report), "report/run-meta.json": digest(meta)})
    else:
        error = next((s.strip() for s in reversed(console.splitlines()) if s.startswith("Ошибка ревью.")), "")
        expected = (name == "truncated" and code == 1 and "прочитать PDF" in error and not report.exists())
        result.update(outcome="ожидаемый отказ" if expected else "сбой", diagnostic=error or "См. протокол CLI.")
    save_complete(dest / "measurement.json", json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    return result["outcome"] != "сбой"


def summarize(folder, corpus):
    header = ["# Проверка на незнакомых документах", "",
              "Время измерено от запуска процесса CLI до его завершения. В таблице приведены результаты отдельных вызовов. Повреждённый PDF проверяет диагностику до обращения к модели.", "",
              "| Документ | Вход, байт | Время, с | Утверждения | Нарушения | Результат |",
              "|---|---:|---:|---:|---:|---|"]
    for name, (filename, label) in CASES.items():
        data = verified_measurement(folder, name, corpus)
        if data is None:
            raise ValueError(f"Нет измерения или не совпала контрольная сумма: {name}.")
        cnt = data["counts"] or {}
        link = os.path.relpath(corpus / "inputs" / filename, folder).replace(os.sep, "/")
        result = f"[Отчёт]({name}/report.md)" if data["outcome"] == "отчёт" else data["outcome"]
        if data["diagnostic"]:
            result += ". " + data["diagnostic"].replace("|", "\\|")
        header.append(f"| [{label}]({link}) | {data['source_bytes']} | {data['elapsed_seconds']:.2f} | "
                      f"{cnt.get('requirements', '—')} | {cnt.get('defects', '—')} | "
                      f"{result} · [Измерение]({name}/measurement.json) · [CLI]({name}/stdout.txt) |")
    save_complete(folder / "summary.md", "\n".join(header) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    cmd = parser.add_mutually_exclusive_group()
    cmd.add_argument("--case", choices=CASES)
    cmd.add_argument("--summary", action="store_true")
    parser.add_argument("--checkout", type=Path, default=ROOT, help="репозиторий, в котором запускается CLI")
    parser.add_argument("--output-dir", type=Path, help="папка результатов относительно --checkout")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    checkout = args.checkout.resolve()
    corpus = checkout / "checks/corpus"
    dest = (checkout / args.output_dir).resolve() if args.output_dir else corpus / "results"
    if args.summary:
        summarize(dest, corpus)
        return 0
    settings = _read_settings(checkout / ".env")
    config = {key: settings.get(key) for key in ("LLM_PROVIDER", "LLM_MODEL", "CODEX_EXTRACT_WORKERS",
                                                 "GEMINI_REQUESTS_PER_MINUTE")}
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=checkout, text=True).strip()
    results = [run_case(name, dest, args.resume, commit, config, checkout) for name in ([args.case] if args.case else CASES)]
    if not args.case:
        summarize(dest, corpus)
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
