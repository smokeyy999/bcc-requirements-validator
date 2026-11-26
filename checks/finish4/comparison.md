# Сравнение трёх прогонов на семи документах

Исходная версия `fa37472`, новая `5669ac8`. Один и тот же оценщик учитывает совпадение категории и всех участков источника. Опубликованы первые полные ответы трёх независимых проходов. Разметка и критерии зафиксированы до проверок. [Исходный протокол](../finish/protocol.md)

| Проход | Дефекты из 15, до → после | Совпадения среди всех карточек, до → после | Вопросы, до → после | Вопросы в контрольных документах, до → после |
|---|---:|---:|---:|---:|
| 1 | 15 → 15 | 15/24 → 15/26 | 21 → 23 | 6 → 7 |
| 2 | 14 → 15 | 14/27 → 15/25 | 24 → 23 | 8 → 7 |
| 3 | 14 → 15 | 14/26 → 15/29 | 23 → 26 | 7 → 9 |

## Что зачтено по каждому дефекту

Ссылки ведут к карточкам новой версии. Прочерк означает, что штатный оценщик не нашёл однозначного совпадения.

| ID дефекта | Прежняя версия, проходов из 3 | Первый | Второй | Третий |
|---|---:|---|---|---|
| D-01 | 3/3 | [Z-001](../../reports/finish4/benchmark-runs/dispatch/r1/report.md#z-001) | [Z-001](../../reports/finish4/benchmark-runs/dispatch/r2/report.md#z-001) | [Z-001](../../reports/finish4/benchmark-runs/dispatch/r3/report.md#z-001) |
| D-02 | 3/3 | [Z-002](../../reports/finish4/benchmark-runs/dispatch/r1/report.md#z-002) | [Z-002](../../reports/finish4/benchmark-runs/dispatch/r2/report.md#z-002) | [Z-002](../../reports/finish4/benchmark-runs/dispatch/r3/report.md#z-002) |
| D-03 | 3/3 | [Z-004](../../reports/finish4/benchmark-runs/dispatch/r1/report.md#z-004) | [Z-005](../../reports/finish4/benchmark-runs/dispatch/r2/report.md#z-005) | [Z-003](../../reports/finish4/benchmark-runs/dispatch/r3/report.md#z-003) |
| D-04 | 3/3 | [Z-006](../../reports/finish4/benchmark-runs/dispatch/r1/report.md#z-006) | [Z-006](../../reports/finish4/benchmark-runs/dispatch/r2/report.md#z-006) | [Z-006](../../reports/finish4/benchmark-runs/dispatch/r3/report.md#z-006) |
| D-05 | 3/3 | [Z-005](../../reports/finish4/benchmark-runs/dispatch/r1/report.md#z-005) | [Z-003](../../reports/finish4/benchmark-runs/dispatch/r2/report.md#z-003) | [Z-004](../../reports/finish4/benchmark-runs/dispatch/r3/report.md#z-004) |
| I-01 | 3/3 | [Z-003](../../reports/finish4/benchmark-runs/irrigation/r1/report.md#z-003) | [Z-004](../../reports/finish4/benchmark-runs/irrigation/r2/report.md#z-004) | [Z-004](../../reports/finish4/benchmark-runs/irrigation/r3/report.md#z-004) |
| I-02 | 3/3 | [Z-006](../../reports/finish4/benchmark-runs/irrigation/r1/report.md#z-006) | [Z-006](../../reports/finish4/benchmark-runs/irrigation/r2/report.md#z-006) | [Z-006](../../reports/finish4/benchmark-runs/irrigation/r3/report.md#z-006) |
| I-03 | 1/3 | [Z-007](../../reports/finish4/benchmark-runs/irrigation/r1/report.md#z-007) | [Z-007](../../reports/finish4/benchmark-runs/irrigation/r2/report.md#z-007) | [Z-007](../../reports/finish4/benchmark-runs/irrigation/r3/report.md#z-007) |
| I-04 | 3/3 | [Z-004](../../reports/finish4/benchmark-runs/irrigation/r1/report.md#z-004) | [Z-005](../../reports/finish4/benchmark-runs/irrigation/r2/report.md#z-005) | [Z-005](../../reports/finish4/benchmark-runs/irrigation/r3/report.md#z-005) |
| I-05 | 3/3 | [Z-009](../../reports/finish4/benchmark-runs/irrigation/r1/report.md#z-009) | [Z-008](../../reports/finish4/benchmark-runs/irrigation/r2/report.md#z-008) | [Z-009](../../reports/finish4/benchmark-runs/irrigation/r3/report.md#z-009) |
| S-01 | 3/3 | [Z-001](../../reports/finish4/benchmark-runs/subtitles/r1/report.md#z-001) | [Z-001](../../reports/finish4/benchmark-runs/subtitles/r2/report.md#z-001) | [Z-001](../../reports/finish4/benchmark-runs/subtitles/r3/report.md#z-001) |
| S-02 | 3/3 | [Z-002](../../reports/finish4/benchmark-runs/subtitles/r1/report.md#z-002) | [Z-002](../../reports/finish4/benchmark-runs/subtitles/r2/report.md#z-002) | [Z-002](../../reports/finish4/benchmark-runs/subtitles/r3/report.md#z-002) |
| S-03 | 3/3 | [Z-003](../../reports/finish4/benchmark-runs/subtitles/r1/report.md#z-003) | [Z-003](../../reports/finish4/benchmark-runs/subtitles/r2/report.md#z-003) | [Z-003](../../reports/finish4/benchmark-runs/subtitles/r3/report.md#z-003) |
| S-04 | 3/3 | [Z-005](../../reports/finish4/benchmark-runs/subtitles/r1/report.md#z-005) | [Z-005](../../reports/finish4/benchmark-runs/subtitles/r2/report.md#z-005) | [Z-005](../../reports/finish4/benchmark-runs/subtitles/r3/report.md#z-005) |
| S-05 | 3/3 | [Z-004](../../reports/finish4/benchmark-runs/subtitles/r1/report.md#z-004) | [Z-004](../../reports/finish4/benchmark-runs/subtitles/r2/report.md#z-004) | [Z-004](../../reports/finish4/benchmark-runs/subtitles/r3/report.md#z-004) |

**Аварийное положение клапана.** Категория «Полнота» для недостающего конечного положения зачтена в одном проходе из трёх на исходной версии `fa37472`, в двух на `e49600f` и во всех трёх на финальной `5669ac8`. [Требование W-4](../../benchmark/irrigation/requirements.md#L9) · [Прежняя версия](../release/comparison.md) · [Предшествующая серия](../finish3/comparison.md)

Метки dev/test в штатном отчёте отражают первоначальное разделение. Разработчики изучали пропуски в обеих частях. Три прохода показывают повторяемость на знакомом корпусе. При каждом запуске модели передавали один исходный документ без эталонной разметки.

[Полные результаты](../../reports/finish4/evaluation.md) · [Незачтённые карточки](../../reports/finish4/evaluation-manual.md) · [Проверка вопросов банковского ТЗ](handoff.md)
