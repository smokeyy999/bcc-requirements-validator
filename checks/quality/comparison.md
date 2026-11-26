# Какие ошибки исправлены на прежнем корпусе

Сравниваются три самостоятельных прохода каждой версии через одни и те же семь документов. Модель, исходники, разметка и правила зачёта одинаковы. В числитель попадает единственная карточка с ожидаемыми категорией и участками текста. Отдельно подсчитаны вопросы автору. Среди дополнительных вопросов бывают полезные уточнения вне разметки. [Правила, зафиксированные до испытания](protocol.md) · [Проверка на новых входах](../blind-qa/comparison.md)

| Версия | Проход | Найдено дефектов | Строгая точность | Всего вопросов | Вопросов в исходных контрольных версиях |
|---|---:|---:|---:|---:|---:|
| [`bf920eb`](../../reports/final/evaluation.md) | 1 | 13/15 | 13/28 (46.4%) | 27 | 8 |
| [`bf920eb`](../../reports/final/evaluation.md) | 2 | 12/15 | 12/32 (37.5%) | 30 | 10 |
| [`bf920eb`](../../reports/final/evaluation.md) | 3 | 12/15 | 12/34 (35.3%) | 32 | 10 |
| [`3018c8e`](../../reports/quality/evaluation.md) | 1 | 13/15 | 13/24 (54.2%) | 23 | 7 |
| [`3018c8e`](../../reports/quality/evaluation.md) | 2 | 13/15 | 13/26 (50.0%) | 24 | 8 |
| [`3018c8e`](../../reports/quality/evaluation.md) | 3 | 14/15 | 14/24 (58.3%) | 23 | 7 |

## Воспроизводимость каждого эталонного дефекта

Каждая цифра означает число проходов, в которых дефект получил строгий зачёт. У ссылки — карточка первого зачтённого прохода новой версии. Если зачёта не было, материалы доступны через сводный отчёт корпуса.

| Эталон | До, из 3 | После, из 3 | Доказательство |
|---|---:|---:|---|
| D-01 | 3 | 3 | [Z-001, проход 1](../../reports/quality/benchmark-runs/dispatch/r1/report.md#z-001) |
| D-02 | 3 | 3 | [Z-003, проход 1](../../reports/quality/benchmark-runs/dispatch/r1/report.md#z-003) |
| D-03 | 3 | 3 | [Z-004, проход 1](../../reports/quality/benchmark-runs/dispatch/r1/report.md#z-004) |
| D-04 | 3 | 2 | [Z-004, проход 2](../../reports/quality/benchmark-runs/dispatch/r2/report.md#z-004) |
| D-05 | 1 | 3 | [Z-006, проход 1](../../reports/quality/benchmark-runs/dispatch/r1/report.md#z-006) |
| I-01 | 3 | 3 | [Z-003, проход 1](../../reports/quality/benchmark-runs/irrigation/r1/report.md#z-003) |
| I-02 | 1 | 1 | [Z-005, проход 3](../../reports/quality/benchmark-runs/irrigation/r3/report.md#z-005) |
| I-03 | 2 | 2 | [Z-006, проход 1](../../reports/quality/benchmark-runs/irrigation/r1/report.md#z-006) |
| I-04 | 0 | 3 | [Z-004, проход 1](../../reports/quality/benchmark-runs/irrigation/r1/report.md#z-004) |
| I-05 | 3 | 3 | [Z-007, проход 1](../../reports/quality/benchmark-runs/irrigation/r1/report.md#z-007) |
| S-01 | 3 | 3 | [Z-001, проход 1](../../reports/quality/benchmark-runs/subtitles/r1/report.md#z-001) |
| S-02 | 3 | 2 | [Z-002, проход 1](../../reports/quality/benchmark-runs/subtitles/r1/report.md#z-002) |
| S-03 | 3 | 3 | [Z-003, проход 1](../../reports/quality/benchmark-runs/subtitles/r1/report.md#z-003) |
| S-04 | 3 | 3 | [Z-005, проход 1](../../reports/quality/benchmark-runs/subtitles/r1/report.md#z-005) |
| S-05 | 3 | 3 | [Z-004, проход 1](../../reports/quality/benchmark-runs/subtitles/r1/report.md#z-004) |

Дополнительные незачтённые карточки включены в построчный разбор. Смысловая проверка вопросов на исходном ТЗ организаторов дана для итоговой версии. [Незачтённые случаи](../../reports/quality/evaluation-manual.md) · [Ревью вопросов на исходном ТЗ](../validated/handoff.md)
