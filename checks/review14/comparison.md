# Три прохода на фиксированном корпусе

Версия `1a9fc9b`. Модель `gpt-6.2-sol` выполнила 21 отдельный запуск. Для каждого из семи документов проверены три разных времени старта, версия кода, хеш исходника и хеш отчёта. Эталонные категории, диапазоны исходного текста и оценщик совпадают с версией `9ce4ce9`. Корпус знаком команде по результатам предыдущих версий.

| Проход | Прежняя версия | Текущая версия | Совпало среди всех карточек | Вопросов в очередях |
|---|---:|---:|---:|---:|
| 1 | 15/15 | 15/15 | 15/26 | 23 |
| 2 | 15/15 | 15/15 | 15/26 | 23 |
| 3 | 15/15 | 15/15 | 15/26 | 23 |

| Дефект | Первый проход | Второй проход | Третий проход |
|---|---|---|---|
| D-01 | [Z-001](../../reports/review14/benchmark-runs/dispatch/r1/report.md#z-001) | [Z-001](../../reports/review14/benchmark-runs/dispatch/r2/report.md#z-001) | [Z-001](../../reports/review14/benchmark-runs/dispatch/r3/report.md#z-001) |
| D-02 | [Z-002](../../reports/review14/benchmark-runs/dispatch/r1/report.md#z-002) | [Z-003](../../reports/review14/benchmark-runs/dispatch/r2/report.md#z-003) | [Z-002](../../reports/review14/benchmark-runs/dispatch/r3/report.md#z-002) |
| D-03 | [Z-003](../../reports/review14/benchmark-runs/dispatch/r1/report.md#z-003) | [Z-004](../../reports/review14/benchmark-runs/dispatch/r2/report.md#z-004) | [Z-005](../../reports/review14/benchmark-runs/dispatch/r3/report.md#z-005) |
| D-04 | [Z-006](../../reports/review14/benchmark-runs/dispatch/r1/report.md#z-006) | [Z-006](../../reports/review14/benchmark-runs/dispatch/r2/report.md#z-006) | [Z-006](../../reports/review14/benchmark-runs/dispatch/r3/report.md#z-006) |
| D-05 | [Z-004](../../reports/review14/benchmark-runs/dispatch/r1/report.md#z-004) | [Z-005](../../reports/review14/benchmark-runs/dispatch/r2/report.md#z-005) | [Z-003](../../reports/review14/benchmark-runs/dispatch/r3/report.md#z-003) |
| I-01 | [Z-003](../../reports/review14/benchmark-runs/irrigation/r1/report.md#z-003) | [Z-003](../../reports/review14/benchmark-runs/irrigation/r2/report.md#z-003) | [Z-004](../../reports/review14/benchmark-runs/irrigation/r3/report.md#z-004) |
| I-02 | [Z-005](../../reports/review14/benchmark-runs/irrigation/r1/report.md#z-005) | [Z-005](../../reports/review14/benchmark-runs/irrigation/r2/report.md#z-005) | [Z-007](../../reports/review14/benchmark-runs/irrigation/r3/report.md#z-007) |
| I-03 | [Z-006](../../reports/review14/benchmark-runs/irrigation/r1/report.md#z-006) | [Z-006](../../reports/review14/benchmark-runs/irrigation/r2/report.md#z-006) | [Z-008](../../reports/review14/benchmark-runs/irrigation/r3/report.md#z-008) |
| I-04 | [Z-004](../../reports/review14/benchmark-runs/irrigation/r1/report.md#z-004) | [Z-004](../../reports/review14/benchmark-runs/irrigation/r2/report.md#z-004) | [Z-005](../../reports/review14/benchmark-runs/irrigation/r3/report.md#z-005) |
| I-05 | [Z-007](../../reports/review14/benchmark-runs/irrigation/r1/report.md#z-007) | [Z-007](../../reports/review14/benchmark-runs/irrigation/r2/report.md#z-007) | [Z-009](../../reports/review14/benchmark-runs/irrigation/r3/report.md#z-009) |
| S-01 | [Z-002](../../reports/review14/benchmark-runs/subtitles/r1/report.md#z-002) | [Z-001](../../reports/review14/benchmark-runs/subtitles/r2/report.md#z-001) | [Z-001](../../reports/review14/benchmark-runs/subtitles/r3/report.md#z-001) |
| S-02 | [Z-003](../../reports/review14/benchmark-runs/subtitles/r1/report.md#z-003) | [Z-002](../../reports/review14/benchmark-runs/subtitles/r2/report.md#z-002) | [Z-002](../../reports/review14/benchmark-runs/subtitles/r3/report.md#z-002) |
| S-03 | [Z-004](../../reports/review14/benchmark-runs/subtitles/r1/report.md#z-004) | [Z-004](../../reports/review14/benchmark-runs/subtitles/r2/report.md#z-004) | [Z-003](../../reports/review14/benchmark-runs/subtitles/r3/report.md#z-003) |
| S-04 | [Z-006](../../reports/review14/benchmark-runs/subtitles/r1/report.md#z-006) | [Z-005](../../reports/review14/benchmark-runs/subtitles/r2/report.md#z-005) | [Z-005](../../reports/review14/benchmark-runs/subtitles/r3/report.md#z-005) |
| S-05 | [Z-005](../../reports/review14/benchmark-runs/subtitles/r1/report.md#z-005) | [Z-003](../../reports/review14/benchmark-runs/subtitles/r2/report.md#z-003) | [Z-004](../../reports/review14/benchmark-runs/subtitles/r3/report.md#z-004) |

В 21 принятом отчёте сверено цитат по исходнику — 393. Число запусков CLI — 22, в том числе с ненулевым кодом завершения — 1. Вопрос об отсутствующем аварийном положении клапана (I-03) получил зачёт по категории «Полнота» в 3 из 3 проходов.

[Штатная оценка](../../reports/review14/evaluation.md) · [Карточки вне эталона](../../reports/review14/evaluation-manual.md) · [Предыдущая серия](../review13/comparison.md)

Журнал отклонённой попытки содержит сообщение «Ошибка ревью. Повторный ответ модели не прошёл проверку: /findings/4: В fix есть число, не подтверждённое цитатами. Исправь правку или задай вопрос с тестом. Исчерпан лимит исправлений. Повторите прогон.» [Журнал отклонения](cli/codex-irrigation-base-r1-attempt-1.txt) · [Принятый повтор](cli/codex-irrigation-base-r1-attempt-2.txt)
