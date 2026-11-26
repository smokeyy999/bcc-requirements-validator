import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

from .engine import review
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
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
                                         dir=path.parent, suffix=".tmp", delete=False) as handle:
            tmp = Path(handle.name)
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        if tmp is not None:
            tmp.unlink(missing_ok=True)


def run(source, output, progress=print):
    clock = time.perf_counter()
    start = datetime.now().astimezone()
    commit, state = version()
    if source.resolve() == output.resolve() or (
        source.is_file() and output.is_file() and source.samefile(output)
    ):
        raise ValueError("Вход и выход совпадают. Укажите для отчёта отдельный путь .md.")
    if output.suffix.lower() != ".md" or output.is_dir():
        raise ValueError("Для отчёта укажите путь к файлу с расширением .md.")
    doc = read_document(source)
    progress(f"Документ «{doc.title}» · исходных блоков {len(doc.blocks)} · SHA-256 {doc.sha256}")
    progress(f"Версия {commit} · рабочая копия {state}")
    provider = get_provider()
    provider.probe()
    progress(f"Доступ подтверждён · {provider.name} · {provider.model}")
    result = review(doc, provider, progress=progress)
    finish = datetime.now().astimezone()
    passport = {
        "started": start.isoformat(timespec="seconds"), "finished": finish.isoformat(timespec="seconds"),
        "seconds": time.perf_counter() - clock, "commit": commit, "state": state,
        "provider": provider.name, "model": provider.model, "origin": origin(source, doc.sha256),
    }
    save_complete(output, render(doc, result, passport, source, output))
    counts = result["counts"]
    progress(f'Готово · утверждений {counts["requirements"]} · нарушений {counts["defects"]} · '
             f'вопросов {counts["questions"]} · {time.perf_counter() - clock:.1f} с')
    progress(f"Отчёт сохранён в {output.as_posix()}")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description="Статическое ревью требований в Markdown или текстовом PDF.")
    parser.add_argument("--input", type=Path, required=True, help="исходный файл .md или .pdf")
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
