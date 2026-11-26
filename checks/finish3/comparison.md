# Сравнение трёх прогонов на семи документах

Исходная версия `fa37472`, новая `e49600f`. Один и тот же оценщик учитывает совпадение категории и всех участков источника. Опубликованы первые полные ответы трёх независимых проходов. Разметка и критерии зафиксированы до проверок. [Исходный протокол](../finish/protocol.md)

| Проход | Дефекты из 15, до → после | Совпадения среди всех карточек, до → после | Вопросы, до → после | Вопросы в контрольных документах, до → после |
|---|---:|---:|---:|---:|
| 1 | 15 → 15 | 15/24 → 15/25 | 21 → 22 | 6 → 6 |
| 2 | 14 → 15 | 14/27 → 15/29 | 24 → 26 | 8 → 8 |
| 3 | 14 → 13 | 14/26 → 13/28 | 23 → 25 | 7 → 7 |

## Что зачтено по каждому дефекту

Ссылки ведут к карточкам новой версии. Прочерк означает, что штатный оценщик не нашёл однозначного совпадения.

| ID дефекта | Прежняя версия, проходов из 3 | Первый | Второй | Третий |
|---|---:|---|---|---|
| D-01 | 3/3 | [Z-002](../../reports/finish3/benchmark-runs/dispatch/r1/report.md#z-002) | [Z-001](../../reports/finish3/benchmark-runs/dispatch/r2/report.md#z-001) | [Z-001](../../reports/finish3/benchmark-runs/dispatch/r3/report.md#z-001) |
| D-02 | 3/3 | [Z-003](../../reports/finish3/benchmark-runs/dispatch/r1/report.md#z-003) | [Z-003](../../reports/finish3/benchmark-runs/dispatch/r2/report.md#z-003) | [Z-002](../../reports/finish3/benchmark-runs/dispatch/r3/report.md#z-002) |
| D-03 | 3/3 | [Z-004](../../reports/finish3/benchmark-runs/dispatch/r1/report.md#z-004) | [Z-004](../../reports/finish3/benchmark-runs/dispatch/r2/report.md#z-004) | [Z-003](../../reports/finish3/benchmark-runs/dispatch/r3/report.md#z-003) |
| D-04 | 3/3 | [Z-006](../../reports/finish3/benchmark-runs/dispatch/r1/report.md#z-006) | [Z-006](../../reports/finish3/benchmark-runs/dispatch/r2/report.md#z-006) | [Z-007](../../reports/finish3/benchmark-runs/dispatch/r3/report.md#z-007) |
| D-05 | 3/3 | [Z-005](../../reports/finish3/benchmark-runs/dispatch/r1/report.md#z-005) | [Z-005](../../reports/finish3/benchmark-runs/dispatch/r2/report.md#z-005) | [Z-005](../../reports/finish3/benchmark-runs/dispatch/r3/report.md#z-005) |
| I-01 | 3/3 | [Z-004](../../reports/finish3/benchmark-runs/irrigation/r1/report.md#z-004) | [Z-005](../../reports/finish3/benchmark-runs/irrigation/r2/report.md#z-005) | — |
| I-02 | 3/3 | [Z-006](../../reports/finish3/benchmark-runs/irrigation/r1/report.md#z-006) | [Z-007](../../reports/finish3/benchmark-runs/irrigation/r2/report.md#z-007) | [Z-007](../../reports/finish3/benchmark-runs/irrigation/r3/report.md#z-007) |
| I-03 | 1/3 | [Z-007](../../reports/finish3/benchmark-runs/irrigation/r1/report.md#z-007) | [Z-008](../../reports/finish3/benchmark-runs/irrigation/r2/report.md#z-008) | — |
| I-04 | 3/3 | [Z-005](../../reports/finish3/benchmark-runs/irrigation/r1/report.md#z-005) | [Z-006](../../reports/finish3/benchmark-runs/irrigation/r2/report.md#z-006) | [Z-005](../../reports/finish3/benchmark-runs/irrigation/r3/report.md#z-005) |
| I-05 | 3/3 | [Z-008](../../reports/finish3/benchmark-runs/irrigation/r1/report.md#z-008) | [Z-009](../../reports/finish3/benchmark-runs/irrigation/r2/report.md#z-009) | [Z-008](../../reports/finish3/benchmark-runs/irrigation/r3/report.md#z-008) |
| S-01 | 3/3 | [Z-001](../../reports/finish3/benchmark-runs/subtitles/r1/report.md#z-001) | [Z-001](../../reports/finish3/benchmark-runs/subtitles/r2/report.md#z-001) | [Z-001](../../reports/finish3/benchmark-runs/subtitles/r3/report.md#z-001) |
| S-02 | 3/3 | [Z-002](../../reports/finish3/benchmark-runs/subtitles/r1/report.md#z-002) | [Z-002](../../reports/finish3/benchmark-runs/subtitles/r2/report.md#z-002) | [Z-003](../../reports/finish3/benchmark-runs/subtitles/r3/report.md#z-003) |
| S-03 | 3/3 | [Z-003](../../reports/finish3/benchmark-runs/subtitles/r1/report.md#z-003) | [Z-004](../../reports/finish3/benchmark-runs/subtitles/r2/report.md#z-004) | [Z-004](../../reports/finish3/benchmark-runs/subtitles/r3/report.md#z-004) |
| S-04 | 3/3 | [Z-005](../../reports/finish3/benchmark-runs/subtitles/r1/report.md#z-005) | [Z-005](../../reports/finish3/benchmark-runs/subtitles/r2/report.md#z-005) | [Z-006](../../reports/finish3/benchmark-runs/subtitles/r3/report.md#z-006) |
| S-05 | 3/3 | [Z-004](../../reports/finish3/benchmark-runs/subtitles/r1/report.md#z-004) | [Z-003](../../reports/finish3/benchmark-runs/subtitles/r2/report.md#z-003) | [Z-005](../../reports/finish3/benchmark-runs/subtitles/r3/report.md#z-005) |

**Аварийное положение клапана.** Категорию «Полнота» для требуемого аварийного положения оценщик подтвердил в 2 из 3 проходов. В предыдущей версии был зачтён один. [Требование W-4](../../benchmark/irrigation/requirements.md#L9) · [Прежнее сравнение](../release/comparison.md)

[Полные результаты](../../reports/finish3/evaluation.md) · [Незачтённые карточки](../../reports/finish3/evaluation-manual.md) · [Проверка вопросов банковского ТЗ](handoff.md)
