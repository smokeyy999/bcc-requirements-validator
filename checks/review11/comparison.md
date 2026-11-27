# Три прохода на фиксированном корпусе

Версия `05ef616`. Модель `gpt-6.2-sol` выполнила 21 отдельный запуск. Для каждого из семи документов проверены три разных времени старта, версия кода, хеш исходника и хеш отчёта. Эталонные категории, диапазоны исходного текста и оценщик совпадают с версией `7db8d3d`. Корпус знаком команде по результатам предыдущих версий.

| Проход | Прежняя версия | Текущая версия | Совпало среди всех карточек | Вопросов в очередях |
|---|---:|---:|---:|---:|
| 1 | 15/15 | 15/15 | 15/26 | 23 |
| 2 | 15/15 | 15/15 | 15/27 | 25 |
| 3 | 15/15 | 15/15 | 15/28 | 25 |

| Дефект | Первый проход | Второй проход | Третий проход |
|---|---|---|---|
| D-01 | [Z-001](../../reports/review11/benchmark-runs/dispatch/r1/report.md#z-001) | [Z-001](../../reports/review11/benchmark-runs/dispatch/r2/report.md#z-001) | [Z-002](../../reports/review11/benchmark-runs/dispatch/r3/report.md#z-002) |
| D-02 | [Z-002](../../reports/review11/benchmark-runs/dispatch/r1/report.md#z-002) | [Z-002](../../reports/review11/benchmark-runs/dispatch/r2/report.md#z-002) | [Z-003](../../reports/review11/benchmark-runs/dispatch/r3/report.md#z-003) |
| D-03 | [Z-005](../../reports/review11/benchmark-runs/dispatch/r1/report.md#z-005) | [Z-005](../../reports/review11/benchmark-runs/dispatch/r2/report.md#z-005) | [Z-004](../../reports/review11/benchmark-runs/dispatch/r3/report.md#z-004) |
| D-04 | [Z-006](../../reports/review11/benchmark-runs/dispatch/r1/report.md#z-006) | [Z-006](../../reports/review11/benchmark-runs/dispatch/r2/report.md#z-006) | [Z-006](../../reports/review11/benchmark-runs/dispatch/r3/report.md#z-006) |
| D-05 | [Z-003](../../reports/review11/benchmark-runs/dispatch/r1/report.md#z-003) | [Z-003](../../reports/review11/benchmark-runs/dispatch/r2/report.md#z-003) | [Z-005](../../reports/review11/benchmark-runs/dispatch/r3/report.md#z-005) |
| I-01 | [Z-004](../../reports/review11/benchmark-runs/irrigation/r1/report.md#z-004) | [Z-005](../../reports/review11/benchmark-runs/irrigation/r2/report.md#z-005) | [Z-004](../../reports/review11/benchmark-runs/irrigation/r3/report.md#z-004) |
| I-02 | [Z-007](../../reports/review11/benchmark-runs/irrigation/r1/report.md#z-007) | [Z-007](../../reports/review11/benchmark-runs/irrigation/r2/report.md#z-007) | [Z-006](../../reports/review11/benchmark-runs/irrigation/r3/report.md#z-006) |
| I-03 | [Z-008](../../reports/review11/benchmark-runs/irrigation/r1/report.md#z-008) | [Z-008](../../reports/review11/benchmark-runs/irrigation/r2/report.md#z-008) | [Z-007](../../reports/review11/benchmark-runs/irrigation/r3/report.md#z-007) |
| I-04 | [Z-005](../../reports/review11/benchmark-runs/irrigation/r1/report.md#z-005) | [Z-006](../../reports/review11/benchmark-runs/irrigation/r2/report.md#z-006) | [Z-005](../../reports/review11/benchmark-runs/irrigation/r3/report.md#z-005) |
| I-05 | [Z-009](../../reports/review11/benchmark-runs/irrigation/r1/report.md#z-009) | [Z-009](../../reports/review11/benchmark-runs/irrigation/r2/report.md#z-009) | [Z-008](../../reports/review11/benchmark-runs/irrigation/r3/report.md#z-008) |
| S-01 | [Z-001](../../reports/review11/benchmark-runs/subtitles/r1/report.md#z-001) | [Z-001](../../reports/review11/benchmark-runs/subtitles/r2/report.md#z-001) | [Z-001](../../reports/review11/benchmark-runs/subtitles/r3/report.md#z-001) |
| S-02 | [Z-002](../../reports/review11/benchmark-runs/subtitles/r1/report.md#z-002) | [Z-002](../../reports/review11/benchmark-runs/subtitles/r2/report.md#z-002) | [Z-002](../../reports/review11/benchmark-runs/subtitles/r3/report.md#z-002) |
| S-03 | [Z-003](../../reports/review11/benchmark-runs/subtitles/r1/report.md#z-003) | [Z-003](../../reports/review11/benchmark-runs/subtitles/r2/report.md#z-003) | [Z-003](../../reports/review11/benchmark-runs/subtitles/r3/report.md#z-003) |
| S-04 | [Z-005](../../reports/review11/benchmark-runs/subtitles/r1/report.md#z-005) | [Z-005](../../reports/review11/benchmark-runs/subtitles/r2/report.md#z-005) | [Z-005](../../reports/review11/benchmark-runs/subtitles/r3/report.md#z-005) |
| S-05 | [Z-004](../../reports/review11/benchmark-runs/subtitles/r1/report.md#z-004) | [Z-004](../../reports/review11/benchmark-runs/subtitles/r2/report.md#z-004) | [Z-004](../../reports/review11/benchmark-runs/subtitles/r3/report.md#z-004) |

В 21 принятом отчёте сверено цитат по исходнику — 384. Число запусков CLI — 21, в том числе с ненулевым кодом завершения — 0. Вопрос об отсутствующем аварийном положении клапана (I-03) получил зачёт по категории «Полнота» в 3 из 3 проходов.

[Штатная оценка](../../reports/review11/evaluation.md) · [Карточки вне эталона](../../reports/review11/evaluation-manual.md) · [Предыдущая серия](../review10/comparison.md)
