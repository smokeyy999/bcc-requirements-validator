# Три прохода на фиксированном корпусе

Версия `ed55df7`. Модель `gpt-6.2-sol` выполнила 21 отдельный запуск. Для каждого из семи документов проверены три разных времени старта, версия кода, хеш исходника и хеш отчёта. Эталонные категории, диапазоны исходного текста и оценщик совпадают с версией `5669ac8`. Корпус знаком команде по результатам предыдущих версий.

| Проход | Прежняя версия | Текущая версия | Совпало среди всех карточек | Вопросов в очередях |
|---|---:|---:|---:|---:|
| 1 | 15/15 | 15/15 | 15/27 | 24 |
| 2 | 15/15 | 15/15 | 15/27 | 24 |
| 3 | 15/15 | 15/15 | 15/28 | 25 |

| Дефект | Первый проход | Второй проход | Третий проход |
|---|---|---|---|
| D-01 | [Z-001](../../reports/review7/benchmark-runs/dispatch/r1/report.md#z-001) | [Z-001](../../reports/review7/benchmark-runs/dispatch/r2/report.md#z-001) | [Z-001](../../reports/review7/benchmark-runs/dispatch/r3/report.md#z-001) |
| D-02 | [Z-003](../../reports/review7/benchmark-runs/dispatch/r1/report.md#z-003) | [Z-002](../../reports/review7/benchmark-runs/dispatch/r2/report.md#z-002) | [Z-002](../../reports/review7/benchmark-runs/dispatch/r3/report.md#z-002) |
| D-03 | [Z-004](../../reports/review7/benchmark-runs/dispatch/r1/report.md#z-004) | [Z-005](../../reports/review7/benchmark-runs/dispatch/r2/report.md#z-005) | [Z-005](../../reports/review7/benchmark-runs/dispatch/r3/report.md#z-005) |
| D-04 | [Z-006](../../reports/review7/benchmark-runs/dispatch/r1/report.md#z-006) | [Z-006](../../reports/review7/benchmark-runs/dispatch/r2/report.md#z-006) | [Z-006](../../reports/review7/benchmark-runs/dispatch/r3/report.md#z-006) |
| D-05 | [Z-005](../../reports/review7/benchmark-runs/dispatch/r1/report.md#z-005) | [Z-003](../../reports/review7/benchmark-runs/dispatch/r2/report.md#z-003) | [Z-003](../../reports/review7/benchmark-runs/dispatch/r3/report.md#z-003) |
| I-01 | [Z-003](../../reports/review7/benchmark-runs/irrigation/r1/report.md#z-003) | [Z-003](../../reports/review7/benchmark-runs/irrigation/r2/report.md#z-003) | [Z-001](../../reports/review7/benchmark-runs/irrigation/r3/report.md#z-001) |
| I-02 | [Z-006](../../reports/review7/benchmark-runs/irrigation/r1/report.md#z-006) | [Z-006](../../reports/review7/benchmark-runs/irrigation/r2/report.md#z-006) | [Z-006](../../reports/review7/benchmark-runs/irrigation/r3/report.md#z-006) |
| I-03 | [Z-007](../../reports/review7/benchmark-runs/irrigation/r1/report.md#z-007) | [Z-007](../../reports/review7/benchmark-runs/irrigation/r2/report.md#z-007) | [Z-007](../../reports/review7/benchmark-runs/irrigation/r3/report.md#z-007) |
| I-04 | [Z-004](../../reports/review7/benchmark-runs/irrigation/r1/report.md#z-004) | [Z-005](../../reports/review7/benchmark-runs/irrigation/r2/report.md#z-005) | [Z-005](../../reports/review7/benchmark-runs/irrigation/r3/report.md#z-005) |
| I-05 | [Z-009](../../reports/review7/benchmark-runs/irrigation/r1/report.md#z-009) | [Z-008](../../reports/review7/benchmark-runs/irrigation/r2/report.md#z-008) | [Z-008](../../reports/review7/benchmark-runs/irrigation/r3/report.md#z-008) |
| S-01 | [Z-001](../../reports/review7/benchmark-runs/subtitles/r1/report.md#z-001) | [Z-001](../../reports/review7/benchmark-runs/subtitles/r2/report.md#z-001) | [Z-001](../../reports/review7/benchmark-runs/subtitles/r3/report.md#z-001) |
| S-02 | [Z-002](../../reports/review7/benchmark-runs/subtitles/r1/report.md#z-002) | [Z-002](../../reports/review7/benchmark-runs/subtitles/r2/report.md#z-002) | [Z-002](../../reports/review7/benchmark-runs/subtitles/r3/report.md#z-002) |
| S-03 | [Z-003](../../reports/review7/benchmark-runs/subtitles/r1/report.md#z-003) | [Z-004](../../reports/review7/benchmark-runs/subtitles/r2/report.md#z-004) | [Z-003](../../reports/review7/benchmark-runs/subtitles/r3/report.md#z-003) |
| S-04 | [Z-005](../../reports/review7/benchmark-runs/subtitles/r1/report.md#z-005) | [Z-005](../../reports/review7/benchmark-runs/subtitles/r2/report.md#z-005) | [Z-005](../../reports/review7/benchmark-runs/subtitles/r3/report.md#z-005) |
| S-05 | [Z-004](../../reports/review7/benchmark-runs/subtitles/r1/report.md#z-004) | [Z-003](../../reports/review7/benchmark-runs/subtitles/r2/report.md#z-003) | [Z-004](../../reports/review7/benchmark-runs/subtitles/r3/report.md#z-004) |

[Штатная оценка](../../reports/review7/evaluation.md) · [Карточки вне эталона](../../reports/review7/evaluation-manual.md) · [Предыдущая серия](../finish4/comparison.md)
