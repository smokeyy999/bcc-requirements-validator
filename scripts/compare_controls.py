"""Compare findings on identical unseeded documents in two real versions."""
import hashlib
import json
from pathlib import Path
import re

from requirements_validator.__main__ import save_complete
from scripts.verify_report import verify


ROOT = Path(__file__).resolve().parents[1]
CASES = (
    ('Индикатор', 'indicator', 'benchmark/indicator/requirements.md', 'reports/benchmark-runs/indicator/r1/report.md'),
    ('Грузовые ведомости', 'dispatch', 'benchmark/dispatch/baseline.md', 'reports/benchmark-runs/dispatch-base/r1/report.md'),
    ('Полив', 'irrigation', 'benchmark/irrigation/baseline.md', 'reports/benchmark-runs/irrigation-base/r1/report.md'),
    ('Субтитры', 'subtitles', 'benchmark/subtitles/baseline.md', 'reports/benchmark-runs/subtitles-base/r1/report.md'),
    ('Сравнение остатков', 'balance', 'checks/corpus/inputs/balance_comparison.md', 'checks/corpus/results/balance_comparison/report.md'),
)


def main():
    from os.path import relpath
    target = ROOT / 'reports/controls.md'

    def link(path, label):
        return f'[{label}]({Path(relpath(path, target.parent)).as_posix()})'

    versions = [set(), set()]
    totals = [[0, 0], [0, 0]]
    rows = []
    for label, case, source_name, new_name in CASES:
        source = ROOT / source_name
        old = ROOT / 'reports/baseline' / f'{case}.md'
        new = ROOT / new_name
        info = json.loads((new.parent / new.stem / 'run-meta.json').read_text(encoding='utf-8'))
        if info['report_sha256'] != hashlib.sha256(new.read_bytes()).hexdigest():
            raise ValueError(f'Несовпадение SHA нового отчёта {case}')
        models = set()
        cells = []
        for i, report in enumerate((old, new)):
            counts = verify(report, source)
            body = report.read_text(encoding='utf-8')
            versions[i].add(re.search(r'\| Коммит реализации \| `([a-f0-9]{40})`', body)[1])
            models.add(re.search(r'\| Провайдер и модель \| (.+) \|', body)[1])
            for j, field in enumerate(('findings', 'defects')):
                totals[i][j] += counts[field]
            cells.append(link(report, f'{counts["findings"]} / {counts["defects"]}'))
        if len(models) != 1:
            raise ValueError(f'На {case} изменилась модель')
        rows.append(f'| {link(source, label)} | {cells[0]} | {cells[1]} |')
    if any(len(v) != 1 for v in versions):
        raise ValueError('Для одной стороны сравнения использованы разные версии кода')
    text = ['# Контроль дополнительных срабатываний', '',
            'На каждом из пяти документов сопоставлены по одному запуску одной модели на старом и новом коде. '
            'Входные байты для пары идентичны. В каждой ячейке указаны все замечания и из них нарушения. '
            'В эти документы намеренно не вносили дефекты. Дополнительные замечания требуют смысловой проверки человеком.', '',
            f'Предыдущая версия `{next(iter(versions[0]))}`. Новая версия `{next(iter(versions[1]))}`.', '',
            '| Исходный документ | До (замечания / нарушения) | После (замечания / нарушения) |',
            '|---|---:|---:|', *rows, f'| **Всего** | **{totals[0][0]} / {totals[0][1]}** | **{totals[1][0]} / {totals[1][1]}** |', '',
            'В новой версии добавлен финансовый контроль и изменена подача результатов. Пары показывают фактический разброс всего процесса. '
            'Один запуск на версию не позволяет приписать изменение отдельной подсказке. На четырёх документах повторные измерения новой версии приведены в [таблицах бенчмарка](evaluation.md).']
    save_complete(target, '\n'.join(text) + '\n')


if __name__ == '__main__':
    main()
