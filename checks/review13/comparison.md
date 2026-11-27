# Три прохода на фиксированном корпусе

Версия `9ce4ce9`. Модель `gpt-6.2-sol` выполнила 21 отдельный запуск. Для каждого из семи документов проверены три разных времени старта, версия кода, хеш исходника и хеш отчёта. Эталонные категории, диапазоны исходного текста и оценщик совпадают с версией `2c34dc0`. Корпус знаком команде по результатам предыдущих версий.

| Проход | Прежняя версия | Текущая версия | Совпало среди всех карточек | Вопросов в очередях |
|---|---:|---:|---:|---:|
| 1 | 15/15 | 15/15 | 15/25 | 22 |
| 2 | 15/15 | 15/15 | 15/28 | 25 |
| 3 | 15/15 | 15/15 | 15/28 | 25 |

| Дефект | Первый проход | Второй проход | Третий проход |
|---|---|---|---|
| D-01 | [Z-001](../../reports/review13/benchmark-runs/dispatch/r1/report.md#z-001) | [Z-001](../../reports/review13/benchmark-runs/dispatch/r2/report.md#z-001) | [Z-001](../../reports/review13/benchmark-runs/dispatch/r3/report.md#z-001) |
| D-02 | [Z-003](../../reports/review13/benchmark-runs/dispatch/r1/report.md#z-003) | [Z-002](../../reports/review13/benchmark-runs/dispatch/r2/report.md#z-002) | [Z-002](../../reports/review13/benchmark-runs/dispatch/r3/report.md#z-002) |
| D-03 | [Z-004](../../reports/review13/benchmark-runs/dispatch/r1/report.md#z-004) | [Z-005](../../reports/review13/benchmark-runs/dispatch/r2/report.md#z-005) | [Z-005](../../reports/review13/benchmark-runs/dispatch/r3/report.md#z-005) |
| D-04 | [Z-006](../../reports/review13/benchmark-runs/dispatch/r1/report.md#z-006) | [Z-006](../../reports/review13/benchmark-runs/dispatch/r2/report.md#z-006) | [Z-006](../../reports/review13/benchmark-runs/dispatch/r3/report.md#z-006) |
| D-05 | [Z-005](../../reports/review13/benchmark-runs/dispatch/r1/report.md#z-005) | [Z-003](../../reports/review13/benchmark-runs/dispatch/r2/report.md#z-003) | [Z-003](../../reports/review13/benchmark-runs/dispatch/r3/report.md#z-003) |
| I-01 | [Z-004](../../reports/review13/benchmark-runs/irrigation/r1/report.md#z-004) | [Z-004](../../reports/review13/benchmark-runs/irrigation/r2/report.md#z-004) | [Z-005](../../reports/review13/benchmark-runs/irrigation/r3/report.md#z-005) |
| I-02 | [Z-006](../../reports/review13/benchmark-runs/irrigation/r1/report.md#z-006) | [Z-007](../../reports/review13/benchmark-runs/irrigation/r2/report.md#z-007) | [Z-007](../../reports/review13/benchmark-runs/irrigation/r3/report.md#z-007) |
| I-03 | [Z-007](../../reports/review13/benchmark-runs/irrigation/r1/report.md#z-007) | [Z-008](../../reports/review13/benchmark-runs/irrigation/r2/report.md#z-008) | [Z-008](../../reports/review13/benchmark-runs/irrigation/r3/report.md#z-008) |
| I-04 | [Z-005](../../reports/review13/benchmark-runs/irrigation/r1/report.md#z-005) | [Z-006](../../reports/review13/benchmark-runs/irrigation/r2/report.md#z-006) | [Z-006](../../reports/review13/benchmark-runs/irrigation/r3/report.md#z-006) |
| I-05 | [Z-008](../../reports/review13/benchmark-runs/irrigation/r1/report.md#z-008) | [Z-009](../../reports/review13/benchmark-runs/irrigation/r2/report.md#z-009) | [Z-009](../../reports/review13/benchmark-runs/irrigation/r3/report.md#z-009) |
| S-01 | [Z-001](../../reports/review13/benchmark-runs/subtitles/r1/report.md#z-001) | [Z-001](../../reports/review13/benchmark-runs/subtitles/r2/report.md#z-001) | [Z-002](../../reports/review13/benchmark-runs/subtitles/r3/report.md#z-002) |
| S-02 | [Z-002](../../reports/review13/benchmark-runs/subtitles/r1/report.md#z-002) | [Z-002](../../reports/review13/benchmark-runs/subtitles/r2/report.md#z-002) | [Z-003](../../reports/review13/benchmark-runs/subtitles/r3/report.md#z-003) |
| S-03 | [Z-004](../../reports/review13/benchmark-runs/subtitles/r1/report.md#z-004) | [Z-003](../../reports/review13/benchmark-runs/subtitles/r2/report.md#z-003) | [Z-005](../../reports/review13/benchmark-runs/subtitles/r3/report.md#z-005) |
| S-04 | [Z-005](../../reports/review13/benchmark-runs/subtitles/r1/report.md#z-005) | [Z-005](../../reports/review13/benchmark-runs/subtitles/r2/report.md#z-005) | [Z-006](../../reports/review13/benchmark-runs/subtitles/r3/report.md#z-006) |
| S-05 | [Z-003](../../reports/review13/benchmark-runs/subtitles/r1/report.md#z-003) | [Z-004](../../reports/review13/benchmark-runs/subtitles/r2/report.md#z-004) | [Z-004](../../reports/review13/benchmark-runs/subtitles/r3/report.md#z-004) |

В 21 принятом отчёте сверено цитат по исходнику — 387. Число запусков CLI — 21, в том числе с ненулевым кодом завершения — 0. Вопрос об отсутствующем аварийном положении клапана (I-03) получил зачёт по категории «Полнота» в 3 из 3 проходов.

[Штатная оценка](../../reports/review13/evaluation.md) · [Карточки вне эталона](../../reports/review13/evaluation-manual.md) · [Предыдущая серия](../review12/comparison.md)
