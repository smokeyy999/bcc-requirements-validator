import argparse
from contextlib import contextmanager
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

from .engine import review
from .metrics import RunMetrics, stage
from .provider import get_provider
from .report import plain, render
from .source import read_document


ROOT = Path(__file__).resolve().parents[1]


def version():
    def git(*args):
        return subprocess.run(
            ["git", *args], cwd=ROOT, capture_output=True, check=True, timeout=8
        ).stdout.decode("utf-8", errors="replace").strip()
    try:
        if Path(git("rev-parse", "--show-toplevel")).resolve() != ROOT:
            return "не определён", "пробный прогон, отдельный репозиторий не найден"
        commit = git("rev-parse", "HEAD")
        dirty = git("status", "--porcelain", "--untracked-files=all")
        return commit, ("есть локальные изменения, пробный прогон" if dirty else "чистая")
    except (OSError, subprocess.SubprocessError):
        return "не определён", "пробный прогон, версия Git недоступна"


def origin(path, digest):
    try:
        manifest = json.loads((ROOT / "docs" / "origin.json").read_text(encoding="utf-8"))
        if manifest["sha256"] == digest:
            return f'[Оригинал организаторов]({manifest["url"]})'
    except (OSError, KeyError, ValueError):
        pass
    return "Файл пользователя · " + plain(path.name)


def save_complete(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(mode="wb", dir=path.parent, suffix=".tmp", delete=False) as handle:
            tmp = Path(handle.name)
            handle.write(content.encode("utf-8") if isinstance(content, str) else content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        if tmp is not None:
            tmp.unlink(missing_ok=True)


@contextmanager
def _publication_lock(output):
    # Один локальный файл блокировки для одного итогового пути, вне репозитория.
    ident = hashlib.sha256(os.path.normcase(str(output.resolve())).encode("utf-8")).hexdigest()
    lock = Path(tempfile.gettempdir()) / f"requirements-review-{ident}.lock"
    with lock.open("a+b") as stream:
        if stream.tell() == 0:
            stream.write(b"0")
            stream.flush()
        stream.seek(0)
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(stream.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        yield  # закрытие дескриптора автоматически освобождает блокировку


def publish(output, content, meta_path, meta):
    with _publication_lock(output):
        # Журнал нужен только на время двух замен. Если процесс был принудительно
        # завершён между ними, следующий запуск восстановит согласованную пару.
        journal = meta_path.with_name(".pending.json")

        def recover():
            pending = json.loads(journal.read_bytes())
            current = hashlib.sha256(output.read_bytes()).hexdigest() if output.is_file() else None
            if current != pending["next_report_sha256"]:
                previous = pending["previous"]
                if previous is None:
                    meta_path.unlink(missing_ok=True)
                else:
                    save_complete(meta_path, previous)
            journal.unlink()

        if journal.exists():
            recover()
        previous = meta_path.read_bytes().decode("utf-8") if meta_path.exists() else None
        save_complete(journal, json.dumps({"previous": previous, "next_report_sha256": meta["report_sha256"]}))
        try:
            save_complete(meta_path, json.dumps(meta, ensure_ascii=False, indent=2) + "\n")
            save_complete(output, content)
        except BaseException:
            recover()
            raise
        journal.unlink()


def run(source, output, progress=print):
    metrics = RunMetrics()
    with metrics.capture():
        return _run(source, output, progress, metrics)


def _run(source, output, progress, metrics):
    clock = time.perf_counter()
    start = datetime.now().astimezone()
    commit, state = version()
    if source.resolve() == output.resolve() or (
        source.is_file() and output.is_file() and source.samefile(output)
    ):
        raise ValueError("Вход и выход совпадают. Укажите для отчёта отдельный путь .md.")
    if output.suffix.lower() != ".md" or output.is_dir():
        raise ValueError("Для отчёта укажите путь к файлу с расширением .md.")
    meta_path = output.parent / output.stem / "run-meta.json"
    if meta_path.parent.exists() and not meta_path.parent.is_dir():
        raise ValueError("Для метрик нужна подпапка с именем отчёта. Выберите другой путь .md.")
    doc = read_document(source)
    progress(f"Документ «{doc.title}» · исходных блоков {len(doc.blocks)} · SHA-256 {doc.sha256}")
    progress(f"Версия {commit} · рабочая копия {state}")
    provider = get_provider()
    stage("probe")
    provider.probe()
    progress(f"Доступ подтверждён · {provider.name} · {provider.model}")
    result = review(doc, provider, progress=progress)
    stage("render")
    finish = datetime.now().astimezone()
    config = provider.configuration()
    before_render = metrics.summary()
    passport = {
        "started": start.isoformat(timespec="seconds"), "finished": finish.isoformat(timespec="seconds"),
        "seconds": time.perf_counter() - clock, "commit": commit, "state": state,
        "provider": provider.name, "model": provider.model, "origin": origin(source, doc.sha256),
        "settings": config, "metrics_path": meta_path.relative_to(output.parent).as_posix(),
        "model_calls": before_render["model_calls"], **before_render["tokens"],
    }
    content = render(doc, result, passport, source, output)
    counts = result["counts"]
    meta = {
        "schema_version": 1, "source": source.name, "source_sha256": doc.sha256,
        "source_blocks": len(doc.blocks), "report": output.name,
        "report_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
        "started_at": passport["started"], "finished_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "provider": provider.name, "model": provider.model, "generation": config,
        "commit": commit, "working_tree": state, **metrics.summary(),
        "elapsed_scope": "От входа в CLI-проверку до подготовки метрики для записи, включая формирование Markdown.",
        "counts": {**counts, "critical_defects": sum(f["counted"] and f["severity"] == "Критичная" for f in result["findings"]),
                   "blocking_questions": sum(q["blocking"] for q in result["questions"])},
    }
    publish(output, content, meta_path, meta)
    progress(f"Отчёт сохранён в {output.as_posix()}")
    progress(f"Метрики сохранены в {meta_path.as_posix()}")
    usage = meta["tokens"]
    input_tokens = usage["input_tokens"] if usage["input_tokens"] is not None else "нет полных данных"
    output_tokens = usage["output_tokens"] if usage["output_tokens"] is not None else "нет полных данных"
    progress(f'Готово за {time.perf_counter() - clock:.1f} с, включая запись · '
             f'запросов модели {meta["model_calls"]} (повторных {meta["retry_model_calls"]}) · '
             f'токены входа {input_tokens}, выхода {output_tokens} · утверждений {counts["requirements"]} · '
             f'нарушений {counts["defects"]} · вопросов {counts["questions"]}')
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description="Статическое ревью требований в Markdown, DOCX или текстовом PDF.")
    parser.add_argument("--input", type=Path, required=True, help="исходный файл .md, .docx или .pdf")
    parser.add_argument("--output", type=Path, required=True, help="путь для полного отчёта .md")
    args = parser.parse_args(argv)
    try:
        run(args.input, args.output, progress=lambda msg: print(msg, flush=True))
    except (OSError, ValueError) as exc:
        print(f"Ошибка ревью. {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Прогон прерван. Повторите команду для полного анализа.", file=sys.stderr)
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
