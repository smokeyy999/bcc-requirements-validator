# Три прохода на фиксированном корпусе

Версия `5e39095`. Модель `gpt-6.2-sol` выполнила 21 отдельный запуск. Для каждого из семи документов проверены три разных времени старта, версия кода, хеш исходника и хеш отчёта. Эталонные категории, диапазоны исходного текста и оценщик совпадают с версией `5669ac8`. Корпус знаком команде по результатам предыдущих версий.

| Проход | Прежняя версия | Текущая версия | Совпало среди всех карточек | Вопросов в очередях |
|---|---:|---:|---:|---:|
| 1 | 15/15 | 15/15 | 15/26 | 23 |
| 2 | 15/15 | 14/15 | 14/24 | 22 |
| 3 | 15/15 | 15/15 | 15/27 | 24 |

| Дефект | Первый проход | Второй проход | Третий проход |
|---|---|---|---|
| D-01 | [Z-001](../../reports/review5/benchmark-runs/dispatch/r1/report.md#z-001) | [Z-001](../../reports/review5/benchmark-runs/dispatch/r2/report.md#z-001) | [Z-001](../../reports/review5/benchmark-runs/dispatch/r3/report.md#z-001) |
| D-02 | [Z-002](../../reports/review5/benchmark-runs/dispatch/r1/report.md#z-002) | [Z-002](../../reports/review5/benchmark-runs/dispatch/r2/report.md#z-002) | [Z-002](../../reports/review5/benchmark-runs/dispatch/r3/report.md#z-002) |
| D-03 | [Z-005](../../reports/review5/benchmark-runs/dispatch/r1/report.md#z-005) | [Z-005](../../reports/review5/benchmark-runs/dispatch/r2/report.md#z-005) | [Z-005](../../reports/review5/benchmark-runs/dispatch/r3/report.md#z-005) |
| D-04 | [Z-006](../../reports/review5/benchmark-runs/dispatch/r1/report.md#z-006) | [Z-006](../../reports/review5/benchmark-runs/dispatch/r2/report.md#z-006) | [Z-006](../../reports/review5/benchmark-runs/dispatch/r3/report.md#z-006) |
| D-05 | [Z-003](../../reports/review5/benchmark-runs/dispatch/r1/report.md#z-003) | [Z-003](../../reports/review5/benchmark-runs/dispatch/r2/report.md#z-003) | [Z-003](../../reports/review5/benchmark-runs/dispatch/r3/report.md#z-003) |
| I-01 | [Z-004](../../reports/review5/benchmark-runs/irrigation/r1/report.md#z-004) | [Z-003](../../reports/review5/benchmark-runs/irrigation/r2/report.md#z-003) | [Z-004](../../reports/review5/benchmark-runs/irrigation/r3/report.md#z-004) |
| I-02 | [Z-006](../../reports/review5/benchmark-runs/irrigation/r1/report.md#z-006) | [Z-006](../../reports/review5/benchmark-runs/irrigation/r2/report.md#z-006) | [Z-006](../../reports/review5/benchmark-runs/irrigation/r3/report.md#z-006) |
| I-03 | [Z-007](../../reports/review5/benchmark-runs/irrigation/r1/report.md#z-007) | [Пропуск](../../reports/review5/benchmark-runs/irrigation/r2/report.md) | [Z-007](../../reports/review5/benchmark-runs/irrigation/r3/report.md#z-007) |
| I-04 | [Z-005](../../reports/review5/benchmark-runs/irrigation/r1/report.md#z-005) | [Z-004](../../reports/review5/benchmark-runs/irrigation/r2/report.md#z-004) | [Z-005](../../reports/review5/benchmark-runs/irrigation/r3/report.md#z-005) |
| I-05 | [Z-008](../../reports/review5/benchmark-runs/irrigation/r1/report.md#z-008) | [Z-007](../../reports/review5/benchmark-runs/irrigation/r2/report.md#z-007) | [Z-008](../../reports/review5/benchmark-runs/irrigation/r3/report.md#z-008) |
| S-01 | [Z-001](../../reports/review5/benchmark-runs/subtitles/r1/report.md#z-001) | [Z-001](../../reports/review5/benchmark-runs/subtitles/r2/report.md#z-001) | [Z-001](../../reports/review5/benchmark-runs/subtitles/r3/report.md#z-001) |
| S-02 | [Z-002](../../reports/review5/benchmark-runs/subtitles/r1/report.md#z-002) | [Z-002](../../reports/review5/benchmark-runs/subtitles/r2/report.md#z-002) | [Z-002](../../reports/review5/benchmark-runs/subtitles/r3/report.md#z-002) |
| S-03 | [Z-004](../../reports/review5/benchmark-runs/subtitles/r1/report.md#z-004) | [Z-003](../../reports/review5/benchmark-runs/subtitles/r2/report.md#z-003) | [Z-003](../../reports/review5/benchmark-runs/subtitles/r3/report.md#z-003) |
| S-04 | [Z-005](../../reports/review5/benchmark-runs/subtitles/r1/report.md#z-005) | [Z-005](../../reports/review5/benchmark-runs/subtitles/r2/report.md#z-005) | [Z-005](../../reports/review5/benchmark-runs/subtitles/r3/report.md#z-005) |
| S-05 | [Z-003](../../reports/review5/benchmark-runs/subtitles/r1/report.md#z-003) | [Z-004](../../reports/review5/benchmark-runs/subtitles/r2/report.md#z-004) | [Z-004](../../reports/review5/benchmark-runs/subtitles/r3/report.md#z-004) |

[Штатная оценка](../../reports/review5/evaluation.md) · [Карточки вне эталона](../../reports/review5/evaluation-manual.md) · [Предыдущая серия](../finish4/comparison.md)
