# Сравнение трёх прогонов на семи документах

Исходная версия `fa37472`, новая `d16b732`. Один и тот же оценщик учитывает совпадение категории и всех участков источника. Опубликованы первые полные ответы трёх независимых проходов. Разметка и критерии зафиксированы до проверок. [Исходный протокол](../finish/protocol.md)

| Проход | Дефекты из 15, до → после | Совпадения среди всех карточек, до → после | Вопросы, до → после | Вопросы в контрольных документах, до → после |
|---|---:|---:|---:|---:|
| 1 | 15 → 13 | 15/24 → 13/28 | 21 → 26 | 6 → 8 |
| 2 | 14 → 14 | 14/27 → 14/28 | 24 → 25 | 8 → 7 |
| 3 | 14 → 15 | 14/26 → 15/25 | 23 → 22 | 7 → 6 |

## Что зачтено по каждому дефекту

Ссылки ведут к карточкам новой версии. Прочерк означает, что штатный оценщик не нашёл однозначного совпадения.

| ID дефекта | Прежняя версия, проходов из 3 | Первый | Второй | Третий |
|---|---:|---|---|---|
| D-01 | 3/3 | [Z-001](../../reports/finish/benchmark-runs/dispatch/r1/report.md#z-001) | [Z-001](../../reports/finish/benchmark-runs/dispatch/r2/report.md#z-001) | [Z-001](../../reports/finish/benchmark-runs/dispatch/r3/report.md#z-001) |
| D-02 | 3/3 | — | [Z-002](../../reports/finish/benchmark-runs/dispatch/r2/report.md#z-002) | [Z-002](../../reports/finish/benchmark-runs/dispatch/r3/report.md#z-002) |
| D-03 | 3/3 | [Z-003](../../reports/finish/benchmark-runs/dispatch/r1/report.md#z-003) | [Z-003](../../reports/finish/benchmark-runs/dispatch/r2/report.md#z-003) | [Z-005](../../reports/finish/benchmark-runs/dispatch/r3/report.md#z-005) |
| D-04 | 3/3 | [Z-006](../../reports/finish/benchmark-runs/dispatch/r1/report.md#z-006) | [Z-006](../../reports/finish/benchmark-runs/dispatch/r2/report.md#z-006) | [Z-006](../../reports/finish/benchmark-runs/dispatch/r3/report.md#z-006) |
| D-05 | 3/3 | [Z-004](../../reports/finish/benchmark-runs/dispatch/r1/report.md#z-004) | [Z-004](../../reports/finish/benchmark-runs/dispatch/r2/report.md#z-004) | [Z-003](../../reports/finish/benchmark-runs/dispatch/r3/report.md#z-003) |
| I-01 | 3/3 | [Z-004](../../reports/finish/benchmark-runs/irrigation/r1/report.md#z-004) | [Z-005](../../reports/finish/benchmark-runs/irrigation/r2/report.md#z-005) | [Z-004](../../reports/finish/benchmark-runs/irrigation/r3/report.md#z-004) |
| I-02 | 3/3 | [Z-007](../../reports/finish/benchmark-runs/irrigation/r1/report.md#z-007) | [Z-007](../../reports/finish/benchmark-runs/irrigation/r2/report.md#z-007) | [Z-006](../../reports/finish/benchmark-runs/irrigation/r3/report.md#z-006) |
| I-03 | 1/3 | [Z-008](../../reports/finish/benchmark-runs/irrigation/r1/report.md#z-008) | — | [Z-007](../../reports/finish/benchmark-runs/irrigation/r3/report.md#z-007) |
| I-04 | 3/3 | [Z-005](../../reports/finish/benchmark-runs/irrigation/r1/report.md#z-005) | [Z-006](../../reports/finish/benchmark-runs/irrigation/r2/report.md#z-006) | [Z-005](../../reports/finish/benchmark-runs/irrigation/r3/report.md#z-005) |
| I-05 | 3/3 | [Z-009](../../reports/finish/benchmark-runs/irrigation/r1/report.md#z-009) | [Z-009](../../reports/finish/benchmark-runs/irrigation/r2/report.md#z-009) | [Z-008](../../reports/finish/benchmark-runs/irrigation/r3/report.md#z-008) |
| S-01 | 3/3 | [Z-002](../../reports/finish/benchmark-runs/subtitles/r1/report.md#z-002) | [Z-002](../../reports/finish/benchmark-runs/subtitles/r2/report.md#z-002) | [Z-001](../../reports/finish/benchmark-runs/subtitles/r3/report.md#z-001) |
| S-02 | 3/3 | [Z-003](../../reports/finish/benchmark-runs/subtitles/r1/report.md#z-003) | [Z-003](../../reports/finish/benchmark-runs/subtitles/r2/report.md#z-003) | [Z-002](../../reports/finish/benchmark-runs/subtitles/r3/report.md#z-002) |
| S-03 | 3/3 | [Z-005](../../reports/finish/benchmark-runs/subtitles/r1/report.md#z-005) | [Z-004](../../reports/finish/benchmark-runs/subtitles/r2/report.md#z-004) | [Z-003](../../reports/finish/benchmark-runs/subtitles/r3/report.md#z-003) |
| S-04 | 3/3 | — | [Z-006](../../reports/finish/benchmark-runs/subtitles/r2/report.md#z-006) | [Z-005](../../reports/finish/benchmark-runs/subtitles/r3/report.md#z-005) |
| S-05 | 3/3 | [Z-006](../../reports/finish/benchmark-runs/subtitles/r1/report.md#z-006) | [Z-005](../../reports/finish/benchmark-runs/subtitles/r2/report.md#z-005) | [Z-004](../../reports/finish/benchmark-runs/subtitles/r3/report.md#z-004) |

**Аварийное положение клапана.** Категорию «Полнота» для требуемого аварийного положения оценщик подтвердил в 2 из 3 проходов. В предыдущей версии был зачтён один. [Требование W-4](../../benchmark/irrigation/requirements.md#L9) · [Прежнее сравнение](../release/comparison.md)

[Полные результаты](../../reports/finish/evaluation.md) · [Незачтённые карточки](../../reports/finish/evaluation-manual.md) · [Проверка вопросов банковского ТЗ](handoff.md)
