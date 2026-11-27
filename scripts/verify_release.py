"""Check the published run metadata, immutable input bytes and complete source citations."""
import argparse
import hashlib
import html
import json
from pathlib import Path
from functools import lru_cache
import re
import subprocess
from urllib.parse import unquote

from requirements_validator.__main__ import save_complete
from requirements_validator.text import text_key
from scripts.verify_report import verify


ROOT = Path(__file__).resolve().parents[1]


def code_objects(root, commit):
    """Read Git object IDs for all agent code and the declared runtime dependencies."""
    rows = subprocess.check_output(
        ["git", "ls-tree", "-z", commit, "--", "requirements_validator", "requirements.txt"],
        cwd=root,
    ).decode("ascii").rstrip("\0").split("\0")
    objects = {}
    for row in rows:
        metadata, path = row.split("\t")
        mode, kind, oid = metadata.split()
        if path == "requirements_validator" and (mode, kind) == ("040000", "tree"):
            objects["validator_tree"] = oid
        elif path == "requirements.txt" and (mode, kind) == ("100644", "blob"):
            objects["requirements_blob"] = oid
    if objects.keys() != {"validator_tree", "requirements_blob"}:
        raise ValueError(f"У версии {commit} отсутствуют код анализатора или файл зависимостей")
    return objects


@lru_cache(maxsize=None)
def verify_revision(root, recorded_commit):
    """Verify the public counterpart when the report records a historical commit."""
    manifest = json.loads((root / "checks/historical-revisions.json").read_bytes())
    if manifest["schema_version"] != 1:
        raise ValueError("Неизвестная версия таблицы соответствия коммитов")
    record = manifest["revisions"].get(recorded_commit)
    if record is None:
        subprocess.run(["git", "cat-file", "-e", recorded_commit + "^{commit}"], cwd=root, check=True)
        return

    public = record["public_commit"]
    if not isinstance(public, str) or not re.fullmatch(r"[0-9a-f]{40}", public):
        raise ValueError(f"Некорректная публичная версия для коммита {recorded_commit}")
    subprocess.run(["git", "merge-base", "--is-ancestor", public, "HEAD"], cwd=root, check=True)
    sources = code_objects(root, public)
    if (sources["validator_tree"] != record["validator_tree"]
            or sources["requirements_blob"] != record["requirements_blob"]):
        raise ValueError(f"Код или зависимости публичной версии {public} расходятся с записью для {recorded_commit}")


def verify_choices(proposal, body, location):
    parts = re.split(r'^\s*(\d+)\. \*\*Вариант (\d+)\.\*\* ', proposal, flags=re.M)
    if '**Вопрос для решения.** ' not in parts[0] or len(parts) < 7:
        raise ValueError(f'{location}: отсутствует вопрос или два варианта решения')
    before = body.split('**Предложение для автора.**', 1)[0]
    evidence = set()
    for ident, block in re.findall(r'^\[(R-[\w-]+)\]\(#r-[\w-]+\) · [^\n]+\n\n((?:> [^\n]*(?:\n|$))+)', before, re.M):
        quote = '\n'.join(line[2:].removesuffix('  ') for line in block.splitlines())
        evidence.add(f'[{ident}](#{ident.lower()}) «{quote}».')
    outcomes = set()
    for index in range(1, len(parts), 3):
        number, label, branch = parts[index:index+3]
        if number != label or number != str(index // 3 + 1):
            raise ValueError(f'{location}: нарушена нумерация вариантов')
        grounding = re.search(r'^\s*\*\*Основание\.\*\* (.+?)\n\n\s*\*\*Ожидаемый результат\.\*\*', branch, re.M | re.S)
        outcome = re.search(r'^\s*\*\*Ожидаемый результат\.\*\* (\S.*)', branch, re.M)
        if not grounding or grounding[1] not in evidence or not outcome or not branch.partition('\n')[0].strip():
            raise ValueError(f'{location}: варианту требуется формулировка, своё основание и наблюдаемый результат')
        outcomes.add(_question_key(outcome[1]))
    if len(outcomes) != (len(parts)-1) // 3:
        raise ValueError(f'{location}: в разных вариантах повторён один ожидаемый результат')


def _question_key(value):
    return text_key(html.unescape(value))


def _check_blocking_groups(text, cards, report):
    section = text.partition('## Вопросы к автору ТЗ\n')[2].partition('<a id="findings">')[0]
    open_ids = {ident for ident, (_, body) in cards.items() if '**Что нужно уточнить.** ' in body}
    for row in re.finditer(r'^Блокирует приёмку · ([^\n]*)$', section, re.M):
        links, separator, _ = row[1].partition('. Зависимый сценарий — ')
        ids = re.findall(r'\[(Z-\d+)\]', links)
        if (not separator or not ids or len(set(ids)) != len(ids) or not set(ids) <= cards.keys()
                or links != ', '.join(f'[{i}](#{i.lower()})' for i in ids)):
            raise ValueError(f'{report}: неверный список карточек блокирующего вопроса')
        if not open_ids.intersection(ids):
            continue
        heading = section[:row.start()].rstrip().split('\n')[-1]
        match = re.fullmatch(r'\*\*(.+)\*\*', heading)
        if not match:
            raise ValueError(f'{report}: отсутствует текст блокирующего вопроса')
        question = _question_key(match[1])
        # The rendered flag belongs to a group (logical OR). No individual flag
        # is present in this format. Require visible support from a different card.
        for ident in set(ids) - open_ids:
            title, body = cards[ident]
            status = body.partition('\n')[0]
            if not re.match(r'^\*\*(?:Дефект|Неоднозначность|Предполагаемый пробел) · [^·\n]+ · (?:Критичная|Существенная)\.\*\*', status):
                continue
            evidence = body.partition('**Предложение для автора.**')[0]
            if not re.search(r'^\[R-[\w-]+\]\(#r-[\w-]+\) · [^\n]+\n\n> \S', evidence, re.M):
                continue
            explicit = re.search(r'^\*\*Вопрос для решения\.\*\* ([^\n]+)', body, re.M)
            # Counted findings publish their own question in the proposal. A
            # gap may only expose it in the title of the card.
            if not explicit and not status.startswith('**Предполагаемый пробел ·'):
                continue
            if _question_key(explicit[1] if explicit else title) == question:
                break
        else:
            raise ValueError(f'{report}: у открытой предпосылки в блокирующей группе {links} нет другого основания для блокирования')


def verify_proposals(text, report, version=1):
    matches = re.findall(r'^### (Z-\d+) · ([^\n]+)\n\n(.*?)(?=^<a id=|\Z)', text, re.M | re.S)
    cards = {ident: (title, body) for ident, title, body in matches}
    if len(matches) != len(cards):
        raise ValueError(f'{report}: повторяется ID карточки')
    if version == 2:
        _check_blocking_groups(text, cards, report)
    checked = 0
    for ident, (_, body) in cards.items():
        if version == 2:
            premise = '**Что нужно уточнить.** ' in body
            conditional = '**Как ответ изменит приёмку.** ' in body
            if premise != conditional or (premise and not body.startswith('**Предполагаемый пробел ·')):
                raise ValueError(f'{report}: {ident} не согласованы статус вопроса, предпосылка и проверка')
            if premise and ' · Критичная.**' in body.partition('\n')[0]:
                raise ValueError(f'{report}: {ident} открытая предпосылка помечена критичной')
        if not body.startswith(('**Дефект ·', '**Неоднозначность ·')):
            continue
        internal_conflict = body.startswith('**Дефект · Противоречивость ·') and '**Внешнее основание.**' not in body
        if version == 2 and internal_conflict:
            condition = re.search(r'^\*\*Общее условие\.\*\* (\S.+?) Основания — (.+?)(?=\n\n|\Z)', body, re.M | re.S)
            if not condition or len(set(re.findall(r'\[(R-[\w-]+)\]', condition[2]))) < 2:
                raise ValueError(f'{report}: {ident} для общего условия требуется опора на обе стороны конфликта')
        proposal = re.search(r'^\*\*Предложение для автора\.\*\* .+?\n\n(.+?)\n\n\*\*Черновик приёмочного теста\.\*\* (\S[^\n]*)', body, re.M | re.S)
        if not proposal:
            raise ValueError(f'{report}: {ident} не содержит предложения и теста')
        if version == 2 and ('**Вариант 1.**' in proposal[1] or body.startswith('**Неоднозначность ·') or internal_conflict):
            verify_choices(proposal[1], body, f'{report}: {ident}')
        elif version == 1 and body.startswith('**Неоднозначность ·'):
            branches = re.findall(r'^\d+\. Для трактовки (\d+) закрепить правило ', proposal[1], re.M)
            interpretations = re.findall(r'^\d+\. ', body.split('**Предложение для автора.**', 1)[0], re.M)
            if len(branches) < 2 or branches != [str(i + 1) for i in range(len(interpretations))]:
                raise ValueError(f'{report}: {ident} не для каждой трактовки указано своё предложение')
        checked += 1
    return checked


def inspect_run(metadata):
    meta = json.loads(metadata.read_text(encoding='utf-8'))
    if meta.get('model') != 'gpt-6.2-sol' or meta.get('provider') != 'OpenAI через Codex CLI':
        raise ValueError(f'{metadata.name}: для комплекта требуется gpt-6.2-sol через Codex CLI')
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
    verify_revision(ROOT, meta['commit'])
    if (f'| Коммит реализации | `{meta["commit"]}` |' not in text
            or f'| Провайдер и модель | {meta["provider"]} · `{meta["model"]}` |' not in text):
        raise ValueError(f'{report}: паспорт версии или модели расходится с метриками')
    counts = verify(report, source)
    version = meta.get('report_format_version', 1)
    if version not in (1, 2):
        raise ValueError(f'{report}: неизвестная версия формата отчёта {version!r}')
    counts['proposals_checked'] = verify_proposals(text, report, version)
    if counts['proposals_checked'] != counts['defects']:
        raise ValueError(f'{report}: число предложений с тестом не совпало с числом нарушений')
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
