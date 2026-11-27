# Три прохода на фиксированном корпусе

Версия `2c34dc0`. Модель `gpt-6.2-sol` выполнила 21 отдельный запуск. Для каждого из семи документов проверены три разных времени старта, версия кода, хеш исходника и хеш отчёта. Эталонные категории, диапазоны исходного текста и оценщик совпадают с версией `05ef616`. Корпус знаком команде по результатам предыдущих версий.

| Проход | Прежняя версия | Текущая версия | Совпало среди всех карточек | Вопросов в очередях |
|---|---:|---:|---:|---:|
| 1 | 15/15 | 15/15 | 15/25 | 22 |
| 2 | 15/15 | 15/15 | 15/27 | 24 |
| 3 | 15/15 | 15/15 | 15/26 | 23 |

| Дефект | Первый проход | Второй проход | Третий проход |
|---|---|---|---|
| D-01 | [Z-001](../../reports/review12/benchmark-runs/dispatch/r1/report.md#z-001) | [Z-001](../../reports/review12/benchmark-runs/dispatch/r2/report.md#z-001) | [Z-001](../../reports/review12/benchmark-runs/dispatch/r3/report.md#z-001) |
| D-02 | [Z-002](../../reports/review12/benchmark-runs/dispatch/r1/report.md#z-002) | [Z-002](../../reports/review12/benchmark-runs/dispatch/r2/report.md#z-002) | [Z-002](../../reports/review12/benchmark-runs/dispatch/r3/report.md#z-002) |
| D-03 | [Z-003](../../reports/review12/benchmark-runs/dispatch/r1/report.md#z-003) | [Z-005](../../reports/review12/benchmark-runs/dispatch/r2/report.md#z-005) | [Z-005](../../reports/review12/benchmark-runs/dispatch/r3/report.md#z-005) |
| D-04 | [Z-006](../../reports/review12/benchmark-runs/dispatch/r1/report.md#z-006) | [Z-006](../../reports/review12/benchmark-runs/dispatch/r2/report.md#z-006) | [Z-006](../../reports/review12/benchmark-runs/dispatch/r3/report.md#z-006) |
| D-05 | [Z-004](../../reports/review12/benchmark-runs/dispatch/r1/report.md#z-004) | [Z-003](../../reports/review12/benchmark-runs/dispatch/r2/report.md#z-003) | [Z-003](../../reports/review12/benchmark-runs/dispatch/r3/report.md#z-003) |
| I-01 | [Z-004](../../reports/review12/benchmark-runs/irrigation/r1/report.md#z-004) | [Z-003](../../reports/review12/benchmark-runs/irrigation/r2/report.md#z-003) | [Z-003](../../reports/review12/benchmark-runs/irrigation/r3/report.md#z-003) |
| I-02 | [Z-006](../../reports/review12/benchmark-runs/irrigation/r1/report.md#z-006) | [Z-006](../../reports/review12/benchmark-runs/irrigation/r2/report.md#z-006) | [Z-006](../../reports/review12/benchmark-runs/irrigation/r3/report.md#z-006) |
| I-03 | [Z-007](../../reports/review12/benchmark-runs/irrigation/r1/report.md#z-007) | [Z-007](../../reports/review12/benchmark-runs/irrigation/r2/report.md#z-007) | [Z-007](../../reports/review12/benchmark-runs/irrigation/r3/report.md#z-007) |
| I-04 | [Z-005](../../reports/review12/benchmark-runs/irrigation/r1/report.md#z-005) | [Z-004](../../reports/review12/benchmark-runs/irrigation/r2/report.md#z-004) | [Z-004](../../reports/review12/benchmark-runs/irrigation/r3/report.md#z-004) |
| I-05 | [Z-008](../../reports/review12/benchmark-runs/irrigation/r1/report.md#z-008) | [Z-009](../../reports/review12/benchmark-runs/irrigation/r2/report.md#z-009) | [Z-009](../../reports/review12/benchmark-runs/irrigation/r3/report.md#z-009) |
| S-01 | [Z-001](../../reports/review12/benchmark-runs/subtitles/r1/report.md#z-001) | [Z-001](../../reports/review12/benchmark-runs/subtitles/r2/report.md#z-001) | [Z-001](../../reports/review12/benchmark-runs/subtitles/r3/report.md#z-001) |
| S-02 | [Z-002](../../reports/review12/benchmark-runs/subtitles/r1/report.md#z-002) | [Z-002](../../reports/review12/benchmark-runs/subtitles/r2/report.md#z-002) | [Z-002](../../reports/review12/benchmark-runs/subtitles/r3/report.md#z-002) |
| S-03 | [Z-004](../../reports/review12/benchmark-runs/subtitles/r1/report.md#z-004) | [Z-003](../../reports/review12/benchmark-runs/subtitles/r2/report.md#z-003) | [Z-003](../../reports/review12/benchmark-runs/subtitles/r3/report.md#z-003) |
| S-04 | [Z-005](../../reports/review12/benchmark-runs/subtitles/r1/report.md#z-005) | [Z-005](../../reports/review12/benchmark-runs/subtitles/r2/report.md#z-005) | [Z-005](../../reports/review12/benchmark-runs/subtitles/r3/report.md#z-005) |
| S-05 | [Z-003](../../reports/review12/benchmark-runs/subtitles/r1/report.md#z-003) | [Z-004](../../reports/review12/benchmark-runs/subtitles/r2/report.md#z-004) | [Z-004](../../reports/review12/benchmark-runs/subtitles/r3/report.md#z-004) |

В 21 принятом отчёте сверено цитат по исходнику — 380. Число запусков CLI — 22, в том числе с ненулевым кодом завершения — 1. Вопрос об отсутствующем аварийном положении клапана (I-03) получил зачёт по категории «Полнота» в 3 из 3 проходов.

[Штатная оценка](../../reports/review12/evaluation.md) · [Карточки вне эталона](../../reports/review12/evaluation-manual.md) · [Предыдущая серия](../review11/comparison.md)

Журнал отклонённой попытки содержит сообщение «Ошибка ревью. Повторный ответ модели не прошёл проверку: /priorities/2: пустой шаг или ссылка на снятое либо постороннее замечание. Повторите прогон.» [Журнал отклонения](cli/codex-dispatch-r2-attempt-1.txt) · [Принятый повтор](cli/codex-dispatch-r2-attempt-2.txt)
