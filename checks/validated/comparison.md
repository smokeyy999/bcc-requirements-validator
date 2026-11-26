# Какие ошибки исправлены на прежнем корпусе

Сравниваются три самостоятельных прохода каждой версии через одни и те же семь документов. Модель, исходники, разметка и правила зачёта одинаковы. В числитель попадает единственная карточка с ожидаемыми категорией и участками текста. Отдельно подсчитаны вопросы автору. Среди дополнительных вопросов бывают полезные уточнения вне разметки. [Правила, зафиксированные до испытания](protocol.md) · [Проверка на новых входах](../holdout/comparison.md)

| Версия | Проход | Найдено дефектов | Строгая точность | Всего вопросов | Вопросов в исходных контрольных версиях |
|---|---:|---:|---:|---:|---:|
| [`bf920eb`](../../reports/final/evaluation.md) | 1 | 13/15 | 13/28 (46.4%) | 27 | 8 |
| [`bf920eb`](../../reports/final/evaluation.md) | 2 | 12/15 | 12/32 (37.5%) | 30 | 10 |
| [`bf920eb`](../../reports/final/evaluation.md) | 3 | 12/15 | 12/34 (35.3%) | 32 | 10 |
| [`31ea961`](../../reports/validated/evaluation.md) | 1 | 12/15 | 12/23 (52.2%) | 22 | 5 |
| [`31ea961`](../../reports/validated/evaluation.md) | 2 | 13/15 | 13/27 (48.1%) | 25 | 7 |
| [`31ea961`](../../reports/validated/evaluation.md) | 3 | 14/15 | 14/26 (53.8%) | 24 | 9 |

## Воспроизводимость каждого эталонного дефекта

Каждая цифра означает число проходов, в которых дефект получил строгий зачёт. У ссылки — карточка первого зачтённого прохода новой версии. Если зачёта не было, материалы доступны через сводный отчёт корпуса.

| Эталон | До, из 3 | После, из 3 | Доказательство |
|---|---:|---:|---|
| D-01 | 3 | 3 | [Z-001, проход 1](../../reports/validated/benchmark-runs/dispatch/r1/report.md#z-001) |
| D-02 | 3 | 3 | [Z-002, проход 1](../../reports/validated/benchmark-runs/dispatch/r1/report.md#z-002) |
| D-03 | 3 | 3 | [Z-005, проход 1](../../reports/validated/benchmark-runs/dispatch/r1/report.md#z-005) |
| D-04 | 3 | 2 | [Z-006, проход 2](../../reports/validated/benchmark-runs/dispatch/r2/report.md#z-006) |
| D-05 | 1 | 3 | [Z-003, проход 1](../../reports/validated/benchmark-runs/dispatch/r1/report.md#z-003) |
| I-01 | 3 | 3 | [Z-004, проход 1](../../reports/validated/benchmark-runs/irrigation/r1/report.md#z-004) |
| I-02 | 1 | 0 | — |
| I-03 | 2 | 1 | [Z-001, проход 3](../../reports/validated/benchmark-runs/irrigation/r3/report.md#z-001) |
| I-04 | 0 | 3 | [Z-005, проход 1](../../reports/validated/benchmark-runs/irrigation/r1/report.md#z-005) |
| I-05 | 3 | 3 | [Z-009, проход 1](../../reports/validated/benchmark-runs/irrigation/r1/report.md#z-009) |
| S-01 | 3 | 3 | [Z-001, проход 1](../../reports/validated/benchmark-runs/subtitles/r1/report.md#z-001) |
| S-02 | 3 | 3 | [Z-002, проход 1](../../reports/validated/benchmark-runs/subtitles/r1/report.md#z-002) |
| S-03 | 3 | 3 | [Z-003, проход 1](../../reports/validated/benchmark-runs/subtitles/r1/report.md#z-003) |
| S-04 | 3 | 3 | [Z-005, проход 1](../../reports/validated/benchmark-runs/subtitles/r1/report.md#z-005) |
| S-05 | 3 | 3 | [Z-004, проход 1](../../reports/validated/benchmark-runs/subtitles/r1/report.md#z-004) |

Дополнительные незачтённые карточки включены в построчный разбор. Семантическая проверка полезности вопросов по исходному ТЗ организаторов приведена в отдельной записке. [Незачтённые случаи](../../reports/validated/evaluation-manual.md) · [Ревью вопросов на исходном ТЗ](handoff.md)
