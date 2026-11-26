# Качество на размеченном корпусе

Дата оценки 2026-11-26T18:41:55+05:00. Провайдер и модель — OpenAI через Codex CLI · gpt-6.2-sol. Коммит реализации — `c0d137edafa74d25c6add7b2505fb657d3164ca6`.

Основной результат измерен по первому запуску каждого документа. Полнота — **14/15 (93.3%)**. Точность — **14/26 (53.8%)**.

Во всех 3 прогонах воспроизвелось **12/50 (24.0%)** групп замечаний.

## Метод

Разметка и базовые версии не включаются в запросы модели. Балл даётся за точную категорию и пересечение цитат со всеми раздельно заданными диапазонами дефекта. Только одна пара «замечание — дефект» может получить балл. Конкурирующие пары и совпадения лишь по строкам остаются незачтёнными. Требования к совпадению зафиксированы до измерения. В знаменатель точности входят все опубликованные карточки Z, включая вопросы и рекомендации. Существование других реальных дефектов, включая контрольные документы, возможно. [Незачтённые замечания для проверки человеком](evaluation-manual.md)

Результаты dev и test приведены отдельно. Dev служит для разработки. Разметка test предназначена для измерения после фиксации механизма и не должна применяться для подбора подсказок.

| Часть | Прогон | Полнота | Точность |
|---|---:|---:|---:|
| all | 1 | 14/15 (93.3%) | 14/26 (53.8%) |
| all | 2 | 13/15 (86.7%) | 13/28 (46.4%) |
| all | 3 | 12/15 (80.0%) | 12/27 (44.4%) |
| dev | 1 | 5/5 (100.0%) | 5/6 (83.3%) |
| dev | 2 | 4/5 (80.0%) | 4/7 (57.1%) |
| dev | 3 | 5/5 (100.0%) | 5/8 (62.5%) |
| test | 1 | 9/10 (90.0%) | 9/20 (45.0%) |
| test | 2 | 9/10 (90.0%) | 9/21 (42.9%) |
| test | 3 | 7/10 (70.0%) | 7/19 (36.8%) |

## Типы дефектов

| Тип | Прогон | Найдено / заложено |
|---|---:|---:|
| дублирование с разными значениями | 1 | 1/1 (100.0%) |
| дублирование с разными значениями | 2 | 1/1 (100.0%) |
| дублирование с разными значениями | 3 | 1/1 (100.0%) |
| неопределённый термин | 1 | 0/1 (0.0%) |
| неопределённый термин | 2 | 0/1 (0.0%) |
| неопределённый термин | 3 | 0/1 (0.0%) |
| непроверяемое нефункциональное требование | 1 | 1/1 (100.0%) |
| непроверяемое нефункциональное требование | 2 | 1/1 (100.0%) |
| непроверяемое нефункциональное требование | 3 | 1/1 (100.0%) |
| несовпадение единиц | 1 | 2/2 (100.0%) |
| несовпадение единиц | 2 | 2/2 (100.0%) |
| несовпадение единиц | 3 | 2/2 (100.0%) |
| отсутствие критерия приёмки | 1 | 1/1 (100.0%) |
| отсутствие критерия приёмки | 2 | 1/1 (100.0%) |
| отсутствие критерия приёмки | 3 | 0/1 (0.0%) |
| отсутствие обработки ошибки | 1 | 1/1 (100.0%) |
| отсутствие обработки ошибки | 2 | 1/1 (100.0%) |
| отсутствие обработки ошибки | 3 | 1/1 (100.0%) |
| противоречие между правилами | 1 | 3/3 (100.0%) |
| противоречие между правилами | 2 | 3/3 (100.0%) |
| противоречие между правилами | 3 | 3/3 (100.0%) |
| разные числа для одного параметра | 1 | 2/2 (100.0%) |
| разные числа для одного параметра | 2 | 1/2 (50.0%) |
| разные числа для одного параметра | 3 | 2/2 (100.0%) |
| расплывчатый срок | 1 | 1/1 (100.0%) |
| расплывчатый срок | 2 | 1/1 (100.0%) |
| расплывчатый срок | 3 | 1/1 (100.0%) |
| ссылка на несуществующий ID | 1 | 2/2 (100.0%) |
| ссылка на несуществующий ID | 2 | 2/2 (100.0%) |
| ссылка на несуществующий ID | 3 | 1/2 (50.0%) |

## Каждый эталон

| ТЗ / часть | ID | Тип | Категория | Строки | Дефект | Прогоны по порядку |
|---|---|---|---|---|---|---|
| dispatch / dev | D-01 | противоречие между правилами | Противоречивость | 6, 7 | Одна и та же ведомость в черновике одновременно допускается и запрещается к передаче. | [Z-001](benchmark-runs/dispatch/r1/report.md#z-001) · [Z-001](benchmark-runs/dispatch/r2/report.md#z-001) · [Z-001](benchmark-runs/dispatch/r3/report.md#z-001) |
| dispatch / dev | D-02 | разные числа для одного параметра | Противоречивость | 10, 11 | Файл из 25 строк принят при максимуме 24. | [Z-002](benchmark-runs/dispatch/r1/report.md#z-002) · пропуск · [Z-002](benchmark-runs/dispatch/r3/report.md#z-002) |
| dispatch / dev | D-03 | расплывчатый срок | Проверяемость | 12 | «Достаточно быстро» не задаёт предела для отображения результата. | [Z-004](benchmark-runs/dispatch/r1/report.md#z-004) · [Z-005](benchmark-runs/dispatch/r2/report.md#z-005) · [Z-004](benchmark-runs/dispatch/r3/report.md#z-004) |
| dispatch / dev | D-04 | ссылка на несуществующий ID | Трассируемость | 13 | Для сообщения об отказе указана отсутствующая норма S-97. | [Z-005](benchmark-runs/dispatch/r1/report.md#z-005) · [Z-006](benchmark-runs/dispatch/r2/report.md#z-006) · [Z-007](benchmark-runs/dispatch/r3/report.md#z-007) |
| dispatch / dev | D-05 | несовпадение единиц | Противоречивость | 15 | Один параметр измеряется в сутках, но его значение интерпретируется как часы. | [Z-003](benchmark-runs/dispatch/r1/report.md#z-003) · [Z-003](benchmark-runs/dispatch/r2/report.md#z-003) · [Z-005](benchmark-runs/dispatch/r3/report.md#z-005) |
| irrigation / test | I-01 | противоречие между правилами | Противоречивость | 6, 7 | Автоматика одновременно игнорирует команду и открывает клапан при ручной остановке. | [Z-004](benchmark-runs/irrigation/r1/report.md#z-004) · [Z-005](benchmark-runs/irrigation/r2/report.md#z-005) · [Z-005](benchmark-runs/irrigation/r3/report.md#z-005) |
| irrigation / test | I-02 | неопределённый термин | Ясность | 8 | Не определены признаки зоны категории омега. | пропуск · пропуск · пропуск |
| irrigation / test | I-03 | отсутствие обработки ошибки | Полнота | 9 | Документ требует аварийного положения клапана, но убрано указание, какое положение выбрать при некорректном датчике. | [Z-007](benchmark-runs/irrigation/r1/report.md#z-007) · [Z-002](benchmark-runs/irrigation/r2/report.md#z-002) · [Z-002](benchmark-runs/irrigation/r3/report.md#z-002) |
| irrigation / test | I-04 | отсутствие критерия приёмки | Полнота | 10 | Обязательному испытанию кнопки не заданы шаг и ожидаемый результат. | [Z-005](benchmark-runs/irrigation/r1/report.md#z-005) · [Z-006](benchmark-runs/irrigation/r2/report.md#z-006) · пропуск |
| irrigation / test | I-05 | дублирование с разными значениями | Противоречивость | 13, 14 | Для одной и той же повторной передачи предписаны три и пять повторов. | [Z-008](benchmark-runs/irrigation/r1/report.md#z-008) · [Z-009](benchmark-runs/irrigation/r2/report.md#z-009) · [Z-008](benchmark-runs/irrigation/r3/report.md#z-008) |
| subtitles / test | S-01 | противоречие между правилами | Противоречивость | 6, 7 | Маркер BOM одновременно обязателен и запрещён. | [Z-001](benchmark-runs/subtitles/r1/report.md#z-001) · [Z-001](benchmark-runs/subtitles/r2/report.md#z-001) · [Z-001](benchmark-runs/subtitles/r3/report.md#z-001) |
| subtitles / test | S-02 | несовпадение единиц | Противоречивость | 8 | 1000 мс названы одной минутой. | [Z-002](benchmark-runs/subtitles/r1/report.md#z-002) · [Z-002](benchmark-runs/subtitles/r2/report.md#z-002) · [Z-002](benchmark-runs/subtitles/r3/report.md#z-002) |
| subtitles / test | S-03 | непроверяемое нефункциональное требование | Проверяемость | 9 | Нет объективного способа принять «effortless to every user». | [Z-003](benchmark-runs/subtitles/r1/report.md#z-003) · [Z-003](benchmark-runs/subtitles/r2/report.md#z-003) · [Z-004](benchmark-runs/subtitles/r3/report.md#z-004) |
| subtitles / test | S-04 | ссылка на несуществующий ID | Трассируемость | 10 | Указан отсутствующий T-40 вместо существующего описания сообщения. | [Z-005](benchmark-runs/subtitles/r1/report.md#z-005) · [Z-005](benchmark-runs/subtitles/r2/report.md#z-005) · пропуск |
| subtitles / test | S-05 | разные числа для одного параметра | Противоречивость | 14, 15 | Тест принимает длину 81 при предельной длине 80. | [Z-004](benchmark-runs/subtitles/r1/report.md#z-004) · [Z-004](benchmark-runs/subtitles/r2/report.md#z-004) · [Z-003](benchmark-runs/subtitles/r3/report.md#z-003) |

## Сохранённые отчёты и контрольные документы

| Отчёт и прогон | Часть | Заложено | Замечаний | Зачтено |
|---|---|---:|---:|---:|
| [dispatch · 1](benchmark-runs/dispatch/r1/report.md) | dev | 5 | 5 | 5 |
| [dispatch · 2](benchmark-runs/dispatch/r2/report.md) | dev | 5 | 6 | 4 |
| [dispatch · 3](benchmark-runs/dispatch/r3/report.md) | dev | 5 | 7 | 5 |
| [dispatch-base · 1](benchmark-runs/dispatch-base/r1/report.md) | dev | 0 | 1 | 0 |
| [dispatch-base · 2](benchmark-runs/dispatch-base/r2/report.md) | dev | 0 | 1 | 0 |
| [dispatch-base · 3](benchmark-runs/dispatch-base/r3/report.md) | dev | 0 | 1 | 0 |
| [indicator · 1](benchmark-runs/indicator/r1/report.md) | test | 0 | 0 | 0 |
| [indicator · 2](benchmark-runs/indicator/r2/report.md) | test | 0 | 0 | 0 |
| [indicator · 3](benchmark-runs/indicator/r3/report.md) | test | 0 | 0 | 0 |
| [irrigation · 1](benchmark-runs/irrigation/r1/report.md) | test | 5 | 9 | 4 |
| [irrigation · 2](benchmark-runs/irrigation/r2/report.md) | test | 5 | 9 | 4 |
| [irrigation · 3](benchmark-runs/irrigation/r3/report.md) | test | 5 | 9 | 3 |
| [irrigation-base · 1](benchmark-runs/irrigation-base/r1/report.md) | test | 0 | 5 | 0 |
| [irrigation-base · 2](benchmark-runs/irrigation-base/r2/report.md) | test | 0 | 5 | 0 |
| [irrigation-base · 3](benchmark-runs/irrigation-base/r3/report.md) | test | 0 | 4 | 0 |
| [subtitles · 1](benchmark-runs/subtitles/r1/report.md) | test | 5 | 5 | 5 |
| [subtitles · 2](benchmark-runs/subtitles/r2/report.md) | test | 5 | 5 | 5 |
| [subtitles · 3](benchmark-runs/subtitles/r3/report.md) | test | 5 | 4 | 4 |
| [subtitles-base · 1](benchmark-runs/subtitles-base/r1/report.md) | test | 0 | 1 | 0 |
| [subtitles-base · 2](benchmark-runs/subtitles-base/r2/report.md) | test | 0 | 2 | 0 |
| [subtitles-base · 3](benchmark-runs/subtitles-base/r3/report.md) | test | 0 | 2 | 0 |

## Воспроизводимость замечаний

В одном документе сравниваются независимо полученные находки одной категории, у которых есть общая строка доказательства во всех вошедших прогонах и не более одного замечания в каждом. Конкурирующие или транзитивные совпадения показаны по отдельности и не дают балла устойчивости.

| ТЗ | Замечание | Категория | Частота | Прогон и ID |
|---|---|---|---:|---|
| dispatch | Отправка черновика | Противоречивость | 1/3 · спорное соответствие | [1/Z-001](benchmark-runs/dispatch/r1/report.md#z-001) |
| dispatch | Отправка ведомости из 25 строк | Противоречивость | 1/3 · спорное соответствие | [1/Z-002](benchmark-runs/dispatch/r1/report.md#z-002) |
| dispatch | Отправка черновика | Противоречивость | 1/3 · спорное соответствие | [2/Z-001](benchmark-runs/dispatch/r2/report.md#z-001) |
| dispatch | Отправка черновика | Противоречивость | 1/3 · спорное соответствие | [3/Z-001](benchmark-runs/dispatch/r3/report.md#z-001) |
| dispatch | Отправка ведомости из 25 строк | Противоречивость | 1/3 · спорное соответствие | [3/Z-002](benchmark-runs/dispatch/r3/report.md#z-002) |
| dispatch | Срок хранения при значении 7 | Противоречивость | 3/3 | [1/Z-003](benchmark-runs/dispatch/r1/report.md#z-003), [2/Z-003](benchmark-runs/dispatch/r2/report.md#z-003), [3/Z-005](benchmark-runs/dispatch/r3/report.md#z-005) |
| dispatch | Пределы задержек | Проверяемость | 1/3 · спорное соответствие | [1/Z-004](benchmark-runs/dispatch/r1/report.md#z-004) |
| dispatch | Срок показа подтверждения | Проверяемость | 1/3 · спорное соответствие | [2/Z-005](benchmark-runs/dispatch/r2/report.md#z-005) |
| dispatch | Задержка индикации передачи | Проверяемость | 1/3 · спорное соответствие | [3/Z-004](benchmark-runs/dispatch/r3/report.md#z-004) |
| dispatch | Критерий немедленной передачи черновика | Проверяемость | 1/3 · спорное соответствие | [3/Z-006](benchmark-runs/dispatch/r3/report.md#z-006) |
| dispatch | Отсутствующая ссылка S-97 | Трассируемость | 3/3 | [1/Z-005](benchmark-runs/dispatch/r1/report.md#z-005), [2/Z-006](benchmark-runs/dispatch/r2/report.md#z-006), [3/Z-007](benchmark-runs/dispatch/r3/report.md#z-007) |
| dispatch | Каковы ожидаемые число и состав строк в сохранённой ведомости после загрузки файла из 25 строк и в ведомости, которую получает перевозчик при отправке из состояния «Готова»? | Полнота | 1/3 | [2/Z-002](benchmark-runs/dispatch/r2/report.md#z-002) |
| dispatch | Если передача черновика предусмотрена, по какому наблюдаемому событию и допустимой задержке после попытки отправки проверять слово «сразу» в S-2? | Полнота | 1/3 | [2/Z-004](benchmark-runs/dispatch/r2/report.md#z-004) |
| dispatch | В каком состоянии должна быть ведомость после подтверждения перевозчика? | Полнота | 1/3 | [3/Z-003](benchmark-runs/dispatch/r3/report.md#z-003) |
| dispatch-base | Три секунды в окне результата | Однозначность | 3/3 | [1/Z-002](benchmark-runs/dispatch-base/r1/report.md#z-002), [2/Z-002](benchmark-runs/dispatch-base/r2/report.md#z-002), [3/Z-002](benchmark-runs/dispatch-base/r3/report.md#z-002) |
| irrigation | Как контроллер должен управлять клапаном при корректных показаниях влажности, если ручная остановка не активна и команды расписания нет? | Полнота | 1/3 · спорное соответствие | [1/Z-001](benchmark-runs/irrigation/r1/report.md#z-001) |
| irrigation | В каком состоянии должен оказаться уже открытый клапан при нажатии кнопки ручной остановки? | Полнота | 1/3 · спорное соответствие | [1/Z-003](benchmark-runs/irrigation/r1/report.md#z-003) |
| irrigation | Вход и результат аварийного сценария | Полнота | 1/3 · спорное соответствие | [1/Z-007](benchmark-runs/irrigation/r1/report.md#z-007) |
| irrigation | Как контроллер должен реагировать на допустимые показания влажности вне ручной остановки и без команды расписания при изначально закрытом клапане? | Полнота | 1/3 · спорное соответствие | [2/Z-001](benchmark-runs/irrigation/r2/report.md#z-001) |
| irrigation | Аварийный переход клапана | Полнота | 1/3 · спорное соответствие | [2/Z-002](benchmark-runs/irrigation/r2/report.md#z-002) |
| irrigation | Какое состояние клапана ожидается после нажатия кнопки ручной остановки, если клапан уже открыт и новых команд нет? | Полнота | 1/3 · спорное соответствие | [2/Z-004](benchmark-runs/irrigation/r2/report.md#z-004) |
| irrigation | Как контроллер должен управлять клапаном по корректным показаниям влажности в штатном режиме? | Полнота | 1/3 · спорное соответствие | [3/Z-001](benchmark-runs/irrigation/r3/report.md#z-001) |
| irrigation | Аварийная реакция на показание датчика | Полнота | 1/3 · спорное соответствие | [3/Z-002](benchmark-runs/irrigation/r3/report.md#z-002) |
| irrigation | В каком положении должен оказаться открытый клапан после нажатия кнопки ручной остановки при отсутствии новых команд открытия? | Полнота | 1/3 · спорное соответствие | [3/Z-004](benchmark-runs/irrigation/r3/report.md#z-004) |
| irrigation | Какое значение должна получать панель и из какого источника контроллер берёт его для передачи? | Полнота | 3/3 | [1/Z-002](benchmark-runs/irrigation/r1/report.md#z-002), [2/Z-003](benchmark-runs/irrigation/r2/report.md#z-003), [3/Z-003](benchmark-runs/irrigation/r3/report.md#z-003) |
| irrigation | Команда расписания при ручной остановке | Противоречивость | 3/3 | [1/Z-004](benchmark-runs/irrigation/r1/report.md#z-004), [2/Z-005](benchmark-runs/irrigation/r2/report.md#z-005), [3/Z-005](benchmark-runs/irrigation/r3/report.md#z-005) |
| irrigation | Какой наблюдаемый результат должен подтвердить прохождение обязательной проверки кнопки «Возобновить» по W-5? | Полнота | 2/3 | [1/Z-005](benchmark-runs/irrigation/r1/report.md#z-005), [2/Z-006](benchmark-runs/irrigation/r2/report.md#z-006) |
| irrigation | По какому признаку или источнику определяется принадлежность зоны к категории омега? | Полнота | 2/3 | [1/Z-006](benchmark-runs/irrigation/r1/report.md#z-006), [2/Z-008](benchmark-runs/irrigation/r2/report.md#z-008) |
| irrigation | Число повторных передач после таймаута | Противоречивость | 3/3 | [1/Z-008](benchmark-runs/irrigation/r1/report.md#z-008), [2/Z-009](benchmark-runs/irrigation/r2/report.md#z-009), [3/Z-008](benchmark-runs/irrigation/r3/report.md#z-008) |
| irrigation | Если по итогам согласования W-1 и W-2 клапан должен открываться, по какому наблюдаемому критерию проверять немедленность открытия? | Полнота | 2/3 | [1/Z-009](benchmark-runs/irrigation/r1/report.md#z-009), [2/Z-007](benchmark-runs/irrigation/r2/report.md#z-007) |
| irrigation | Проверка кнопки «Возобновить» | Проверяемость | 1/3 | [3/Z-006](benchmark-runs/irrigation/r3/report.md#z-006) |
| irrigation | Принадлежность зоны к категории «омега» | Однозначность | 1/3 | [3/Z-007](benchmark-runs/irrigation/r3/report.md#z-007) |
| irrigation | Срок открытия по расписанию | Проверяемость | 1/3 | [3/Z-009](benchmark-runs/irrigation/r3/report.md#z-009) |
| irrigation-base | Как контроллер должен управлять клапаном по корректным показаниям влажности и от каких условий зависит результат? | Полнота | 1/3 · спорное соответствие | [1/Z-001](benchmark-runs/irrigation-base/r1/report.md#z-001) |
| irrigation-base | Каким должно быть положение уже открытого клапана после нажатия кнопки ручной остановки до поступления новых команд? | Полнота | 1/3 · спорное соответствие | [1/Z-004](benchmark-runs/irrigation-base/r1/report.md#z-004) |
| irrigation-base | Должны ли допустимые показания влажности влиять на открытие закрытого клапана при выбранной зоне и снятой ручной остановке? Если да, при каких условиях? | Полнота | 1/3 · спорное соответствие | [2/Z-003](benchmark-runs/irrigation-base/r2/report.md#z-003) |
| irrigation-base | В каком положении должен быть клапан после нажатия кнопки ручной остановки, если до нажатия он был открыт и новых команд ещё не поступило? | Полнота | 1/3 · спорное соответствие | [2/Z-004](benchmark-runs/irrigation-base/r2/report.md#z-004) |
| irrigation-base | При каких условиях допустимое показание влажности влияет на управление клапаном и какое действие ожидается в каждом случае? | Полнота | 1/3 · спорное соответствие | [3/Z-003](benchmark-runs/irrigation-base/r3/report.md#z-003) |
| irrigation-base | Какое состояние должен принять уже открытый клапан после нажатия кнопки ручной остановки, до поступления следующей команды? | Полнота | 1/3 · спорное соответствие | [3/Z-004](benchmark-runs/irrigation-base/r3/report.md#z-004) |
| irrigation-base | Какое значение должна получить панель при повторной передаче и из каких данных или состояния контроллера оно определяется? | Полнота | 3/3 | [1/Z-002](benchmark-runs/irrigation-base/r1/report.md#z-002), [2/Z-001](benchmark-runs/irrigation-base/r2/report.md#z-001), [3/Z-001](benchmark-runs/irrigation-base/r3/report.md#z-001) |
| irrigation-base | По каким признакам полученное показание датчика считается некорректным для применения W-4? | Полнота | 2/3 | [1/Z-003](benchmark-runs/irrigation-base/r1/report.md#z-003), [3/Z-002](benchmark-runs/irrigation-base/r3/report.md#z-002) |
| irrigation-base | Дубль нормы повторной передачи | Дублирование | 2/3 | [1/Z-006](benchmark-runs/irrigation-base/r1/report.md#z-006), [2/Z-005](benchmark-runs/irrigation-base/r2/report.md#z-005) |
| irrigation-base | Критерии некорректного показания | Проверяемость | 1/3 | [2/Z-002](benchmark-runs/irrigation-base/r2/report.md#z-002) |
| subtitles | BOM в начале файла | Противоречивость | 3/3 | [1/Z-001](benchmark-runs/subtitles/r1/report.md#z-001), [2/Z-001](benchmark-runs/subtitles/r2/report.md#z-001), [3/Z-001](benchmark-runs/subtitles/r3/report.md#z-001) |
| subtitles | Шкала временных меток | Противоречивость | 3/3 | [1/Z-002](benchmark-runs/subtitles/r1/report.md#z-002), [2/Z-002](benchmark-runs/subtitles/r2/report.md#z-002), [3/Z-002](benchmark-runs/subtitles/r3/report.md#z-002) |
| subtitles | Критерий простоты экспорта | Проверяемость | 3/3 | [1/Z-003](benchmark-runs/subtitles/r1/report.md#z-003), [2/Z-003](benchmark-runs/subtitles/r2/report.md#z-003), [3/Z-004](benchmark-runs/subtitles/r3/report.md#z-004) |
| subtitles | Длина реплики в приёмочном примере | Противоречивость | 3/3 | [1/Z-004](benchmark-runs/subtitles/r1/report.md#z-004), [2/Z-004](benchmark-runs/subtitles/r2/report.md#z-004), [3/Z-003](benchmark-runs/subtitles/r3/report.md#z-003) |
| subtitles | Битая ссылка на сообщение | Трассируемость | 2/3 | [1/Z-005](benchmark-runs/subtitles/r1/report.md#z-005), [2/Z-005](benchmark-runs/subtitles/r2/report.md#z-005) |
| subtitles-base | Каким должен быть результат команды и состояние свободного пути назначения при экспорте дорожки с репликами длиной 80 и 81 кодовая точка? | Полнота | 3/3 | [1/Z-001](benchmark-runs/subtitles-base/r1/report.md#z-001), [2/Z-001](benchmark-runs/subtitles-base/r2/report.md#z-001), [3/Z-002](benchmark-runs/subtitles-base/r3/report.md#z-002) |
| subtitles-base | По какому признаку формата экспорта приёмочный тест должен проверять, что каждое поле временной метки объявляет миллисекунды? | Полнота | 2/3 | [2/Z-002](benchmark-runs/subtitles-base/r2/report.md#z-002), [3/Z-003](benchmark-runs/subtitles-base/r3/report.md#z-003) |
