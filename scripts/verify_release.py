"""Check the published run metadata, immutable input bytes and complete source citations."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote

from requirements_validator.__main__ import save_complete
from scripts.verify_report import verify


ROOT = Path(__file__).resolve().parents[1]


def inspect_run(metadata):
    meta = json.loads(metadata.read_text(encoding='utf-8'))
    report = metadata.parent.parent / meta['report']
    if report.resolve().parent != metadata.resolve().parent.parent:
        raise ValueError(f'{metadata}: неправильный путь отчёта')
    if meta['working_tree'] != 'чистая':
        raise ValueError(f'{report.name}: прогон помечен пробным')
    body = report.read_bytes()
    if hashlib.sha256(body).hexdigest() != meta['report_sha256']:
        raise ValueError(f'{report}: SHA-256 отчёта отличается от метрик')
    text = body.decode('utf-8')
    original = re.search(r'^\| Входной файл \| \[[^\]]+\]\(([^)]+)\) \|$', text, re.M)
    if not original:
        raise ValueError(f'{report}: отсутствует путь исходника')
    source = (report.parent / unquote(original[1])).resolve()
    if not source.is_relative_to(ROOT) or hashlib.sha256(source.read_bytes()).hexdigest() != meta['source_sha256']:
        raise ValueError(f'{report}: неверный источник')
    if not re.fullmatch(r'[a-f0-9]{40}', meta['commit']):
        raise ValueError(f'{report}: неверный формат версии')
    subprocess.run(['git', 'cat-file', '-e', meta['commit'] + '^{commit}'], cwd=ROOT, check=True)
    if (f'| Коммит реализации | `{meta["commit"]}` |' not in text
            or f'| Провайдер и модель | {meta["provider"]} · `{meta["model"]}` |' not in text):
        raise ValueError(f'{report}: паспорт версии или модели расходится с метриками')
    counts = verify(report, source)
    for name in ('requirements', 'defects', 'critical_defects', 'questions', 'blocking_questions'):
        if counts[name] != meta['counts'][name]:
            raise ValueError(f'{report}: различаются счётчики {name}')
    calls = [row for row in meta['requests'] if row['operation'] == 'generation']
    if len(calls) != meta['model_calls'] or not calls:
        raise ValueError(f'{report}: счётчик вызовов модели не подтверждается журналом')
    for field in ('input_tokens', 'output_tokens'):
        numbers = [row.get(field) for row in calls]
        total = sum(numbers) if all(type(v) is int for v in numbers) else None
        if total != meta['tokens'][field]:
            raise ValueError(f'{report}: счётчик {field} расходится с журналом')
    return dict(report=report.relative_to(ROOT).as_posix(), source=source.relative_to(ROOT).as_posix(),
                commit=meta['commit'], provider=meta['provider'], model=meta['model'], **counts)


def main():
    parser = argparse.ArgumentParser(description='Проверить цитаты, ссылки, хэши и метрики опубликованных прогонов.')
    parser.add_argument('--output', type=Path, help='сохранить результат проверки в JSON')
    args = parser.parse_args()
    files = sorted(p for area in ('reports', 'checks') for p in (ROOT / area).rglob('run-meta.json'))
    if not files:
        parser.exit(1, 'Метрики прогонов не найдены.\n')
    try:
        reports = [inspect_run(p) for p in files]
    except (AssertionError, KeyError, IndexError, ValueError, OSError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f'Проверка не пройдена: {exc}\n')
    result = dict(reports_checked=len(reports), quotes_checked=sum(c['quotes'] for c in reports), reports=reports)
    if args.output:
        save_complete(args.output, json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(f'Проверены паспорта и метрики {len(reports)} прогонов, дословность {result["quotes_checked"]} цитат и их адреса.')


if __name__ == '__main__':
    main()
