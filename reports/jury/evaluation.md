# Качество на размеченном корпусе

Дата оценки 2026-11-26T20:59:42+05:00. Провайдер и модель — OpenAI через Codex CLI · gpt-6.2-sol. Коммит реализации — `78864ebc263344838d5e69dee4d8ea9fbe9df6fe`.

Основной результат измерен по первому запуску каждого документа. Полнота — **13/15 (86.7%)**. Точность — **13/29 (44.8%)**.

Во всех 3 прогонах воспроизвелось **15/52 (28.8%)** групп замечаний.

## Метод

Разметка и базовые версии не включаются в запросы модели. Балл даётся за точную категорию и пересечение цитат со всеми раздельно заданными диапазонами дефекта. Только одна пара «замечание — дефект» может получить балл. Конкурирующие пары и совпадения лишь по строкам остаются незачтёнными. Требования к совпадению зафиксированы до измерения. В знаменатель точности входят все опубликованные карточки Z, включая вопросы и рекомендации. Существование других реальных дефектов, включая контрольные документы, возможно. [Незачтённые замечания для проверки человеком](evaluation-manual.md)

Результаты dev и test приведены отдельно. Dev служит для разработки. Разметка test предназначена для измерения после фиксации механизма и не должна применяться для подбора подсказок.

| Часть | Прогон | Полнота | Точность |
|---|---:|---:|---:|
| all | 1 | 13/15 (86.7%) | 13/29 (44.8%) |
| all | 2 | 11/15 (73.3%) | 11/26 (42.3%) |
| all | 3 | 11/15 (73.3%) | 11/31 (35.5%) |
| dev | 1 | 4/5 (80.0%) | 4/7 (57.1%) |
| dev | 2 | 3/5 (60.0%) | 3/7 (42.9%) |
| dev | 3 | 4/5 (80.0%) | 4/8 (50.0%) |
| test | 1 | 9/10 (90.0%) | 9/22 (40.9%) |
| test | 2 | 8/10 (80.0%) | 8/19 (42.1%) |
| test | 3 | 7/10 (70.0%) | 7/23 (30.4%) |

## Типы дефектов

| Тип | Прогон | Найдено / заложено |
|---|---:|---:|
| дублирование с разными значениями | 1 | 1/1 (100.0%) |
| дублирование с разными значениями | 2 | 1/1 (100.0%) |
| дублирование с разными значениями | 3 | 1/1 (100.0%) |
| неопределённый термин | 1 | 1/1 (100.0%) |
| неопределённый термин | 2 | 1/1 (100.0%) |
| неопределённый термин | 3 | 1/1 (100.0%) |
| непроверяемое нефункциональное требование | 1 | 1/1 (100.0%) |
| непроверяемое нефункциональное требование | 2 | 1/1 (100.0%) |
| непроверяемое нефункциональное требование | 3 | 1/1 (100.0%) |
| несовпадение единиц | 1 | 1/2 (50.0%) |
| несовпадение единиц | 2 | 0/2 (0.0%) |
| несовпадение единиц | 3 | 1/2 (50.0%) |
| отсутствие критерия приёмки | 1 | 0/1 (0.0%) |
| отсутствие критерия приёмки | 2 | 0/1 (0.0%) |
| отсутствие критерия приёмки | 3 | 0/1 (0.0%) |
| отсутствие обработки ошибки | 1 | 1/1 (100.0%) |
| отсутствие обработки ошибки | 2 | 1/1 (100.0%) |
| отсутствие обработки ошибки | 3 | 0/1 (0.0%) |
| противоречие между правилами | 1 | 3/3 (100.0%) |
| противоречие между правилами | 2 | 3/3 (100.0%) |
| противоречие между правилами | 3 | 3/3 (100.0%) |
| разные числа для одного параметра | 1 | 2/2 (100.0%) |
| разные числа для одного параметра | 2 | 1/2 (50.0%) |
| разные числа для одного параметра | 3 | 1/2 (50.0%) |
| расплывчатый срок | 1 | 1/1 (100.0%) |
| расплывчатый срок | 2 | 1/1 (100.0%) |
| расплывчатый срок | 3 | 1/1 (100.0%) |
| ссылка на несуществующий ID | 1 | 2/2 (100.0%) |
| ссылка на несуществующий ID | 2 | 2/2 (100.0%) |
| ссылка на несуществующий ID | 3 | 2/2 (100.0%) |

## Каждый эталон

| ТЗ / часть | ID | Тип | Категория | Строки | Дефект | Прогоны по порядку |
|---|---|---|---|---|---|---|
| dispatch / dev | D-01 | противоречие между правилами | Противоречивость | 6, 7 | Одна и та же ведомость в черновике одновременно допускается и запрещается к передаче. | [Z-001](benchmark-runs/dispatch/r1/report.md#z-001) · [Z-001](benchmark-runs/dispatch/r2/report.md#z-001) · [Z-001](benchmark-runs/dispatch/r3/report.md#z-001) |
| dispatch / dev | D-02 | разные числа для одного параметра | Противоречивость | 10, 11 | Файл из 25 строк принят при максимуме 24. | [Z-004](benchmark-runs/dispatch/r1/report.md#z-004) · пропуск · пропуск |
| dispatch / dev | D-03 | расплывчатый срок | Проверяемость | 12 | «Достаточно быстро» не задаёт предела для отображения результата. | [Z-005](benchmark-runs/dispatch/r1/report.md#z-005) · [Z-003](benchmark-runs/dispatch/r2/report.md#z-003) · [Z-005](benchmark-runs/dispatch/r3/report.md#z-005) |
| dispatch / dev | D-04 | ссылка на несуществующий ID | Трассируемость | 13 | Для сообщения об отказе указана отсутствующая норма S-97. | [Z-007](benchmark-runs/dispatch/r1/report.md#z-007) · [Z-006](benchmark-runs/dispatch/r2/report.md#z-006) · [Z-007](benchmark-runs/dispatch/r3/report.md#z-007) |
| dispatch / dev | D-05 | несовпадение единиц | Противоречивость | 15 | Один параметр измеряется в сутках, но его значение интерпретируется как часы. | пропуск · пропуск · [Z-006](benchmark-runs/dispatch/r3/report.md#z-006) |
| irrigation / test | I-01 | противоречие между правилами | Противоречивость | 6, 7 | Автоматика одновременно игнорирует команду и открывает клапан при ручной остановке. | [Z-004](benchmark-runs/irrigation/r1/report.md#z-004) · [Z-005](benchmark-runs/irrigation/r2/report.md#z-005) · [Z-004](benchmark-runs/irrigation/r3/report.md#z-004) |
| irrigation / test | I-02 | неопределённый термин | Ясность | 8 | Не определены признаки зоны категории омега. | [Z-007](benchmark-runs/irrigation/r1/report.md#z-007) · [Z-007](benchmark-runs/irrigation/r2/report.md#z-007) · [Z-006](benchmark-runs/irrigation/r3/report.md#z-006) |
| irrigation / test | I-03 | отсутствие обработки ошибки | Полнота | 9 | Документ требует аварийного положения клапана, но убрано указание, какое положение выбрать при некорректном датчике. | [Z-008](benchmark-runs/irrigation/r1/report.md#z-008) · [Z-002](benchmark-runs/irrigation/r2/report.md#z-002) · пропуск |
| irrigation / test | I-04 | отсутствие критерия приёмки | Полнота | 10 | Обязательному испытанию кнопки не заданы шаг и ожидаемый результат. | пропуск · пропуск · пропуск |
| irrigation / test | I-05 | дублирование с разными значениями | Противоречивость | 13, 14 | Для одной и той же повторной передачи предписаны три и пять повторов. | [Z-009](benchmark-runs/irrigation/r1/report.md#z-009) · [Z-008](benchmark-runs/irrigation/r2/report.md#z-008) · [Z-009](benchmark-runs/irrigation/r3/report.md#z-009) |
| subtitles / test | S-01 | противоречие между правилами | Противоречивость | 6, 7 | Маркер BOM одновременно обязателен и запрещён. | [Z-002](benchmark-runs/subtitles/r1/report.md#z-002) · [Z-001](benchmark-runs/subtitles/r2/report.md#z-001) · [Z-001](benchmark-runs/subtitles/r3/report.md#z-001) |
| subtitles / test | S-02 | несовпадение единиц | Противоречивость | 8 | 1000 мс названы одной минутой. | [Z-003](benchmark-runs/subtitles/r1/report.md#z-003) · пропуск · пропуск |
| subtitles / test | S-03 | непроверяемое нефункциональное требование | Проверяемость | 9 | Нет объективного способа принять «effortless to every user». | [Z-001](benchmark-runs/subtitles/r1/report.md#z-001) · [Z-003](benchmark-runs/subtitles/r2/report.md#z-003) · [Z-003](benchmark-runs/subtitles/r3/report.md#z-003) |
| subtitles / test | S-04 | ссылка на несуществующий ID | Трассируемость | 10 | Указан отсутствующий T-40 вместо существующего описания сообщения. | [Z-005](benchmark-runs/subtitles/r1/report.md#z-005) · [Z-005](benchmark-runs/subtitles/r2/report.md#z-005) · [Z-005](benchmark-runs/subtitles/r3/report.md#z-005) |
| subtitles / test | S-05 | разные числа для одного параметра | Противоречивость | 14, 15 | Тест принимает длину 81 при предельной длине 80. | [Z-004](benchmark-runs/subtitles/r1/report.md#z-004) · [Z-004](benchmark-runs/subtitles/r2/report.md#z-004) · [Z-004](benchmark-runs/subtitles/r3/report.md#z-004) |

## Сохранённые отчёты и контрольные документы

| Отчёт и прогон | Часть | Заложено | Замечаний | Зачтено |
|---|---|---:|---:|---:|
| [dispatch · 1](benchmark-runs/dispatch/r1/report.md) | dev | 5 | 6 | 4 |
| [dispatch · 2](benchmark-runs/dispatch/r2/report.md) | dev | 5 | 5 | 3 |
| [dispatch · 3](benchmark-runs/dispatch/r3/report.md) | dev | 5 | 7 | 4 |
| [dispatch-base · 1](benchmark-runs/dispatch-base/r1/report.md) | dev | 0 | 1 | 0 |
| [dispatch-base · 2](benchmark-runs/dispatch-base/r2/report.md) | dev | 0 | 2 | 0 |
| [dispatch-base · 3](benchmark-runs/dispatch-base/r3/report.md) | dev | 0 | 1 | 0 |
| [indicator · 1](benchmark-runs/indicator/r1/report.md) | test | 0 | 0 | 0 |
| [indicator · 2](benchmark-runs/indicator/r2/report.md) | test | 0 | 0 | 0 |
| [indicator · 3](benchmark-runs/indicator/r3/report.md) | test | 0 | 0 | 0 |
| [irrigation · 1](benchmark-runs/irrigation/r1/report.md) | test | 5 | 9 | 4 |
| [irrigation · 2](benchmark-runs/irrigation/r2/report.md) | test | 5 | 9 | 4 |
| [irrigation · 3](benchmark-runs/irrigation/r3/report.md) | test | 5 | 10 | 3 |
| [irrigation-base · 1](benchmark-runs/irrigation-base/r1/report.md) | test | 0 | 6 | 0 |
| [irrigation-base · 2](benchmark-runs/irrigation-base/r2/report.md) | test | 0 | 4 | 0 |
| [irrigation-base · 3](benchmark-runs/irrigation-base/r3/report.md) | test | 0 | 5 | 0 |
| [subtitles · 1](benchmark-runs/subtitles/r1/report.md) | test | 5 | 5 | 5 |
| [subtitles · 2](benchmark-runs/subtitles/r2/report.md) | test | 5 | 4 | 4 |
| [subtitles · 3](benchmark-runs/subtitles/r3/report.md) | test | 5 | 5 | 4 |
| [subtitles-base · 1](benchmark-runs/subtitles-base/r1/report.md) | test | 0 | 2 | 0 |
| [subtitles-base · 2](benchmark-runs/subtitles-base/r2/report.md) | test | 0 | 2 | 0 |
| [subtitles-base · 3](benchmark-runs/subtitles-base/r3/report.md) | test | 0 | 3 | 0 |

## Воспроизводимость замечаний

В одном документе сравниваются независимо полученные находки одной категории, у которых есть общая строка доказательства во всех вошедших прогонах и не более одного замечания в каждом. Конкурирующие или транзитивные совпадения показаны по отдельности и не дают балла устойчивости.

| ТЗ | Замечание | Категория | Частота | Прогон и ID |
|---|---|---|---:|---|
| dispatch | Отправка черновика | Противоречивость | 3/3 | [1/Z-001](benchmark-runs/dispatch/r1/report.md#z-001), [2/Z-001](benchmark-runs/dispatch/r2/report.md#z-001), [3/Z-001](benchmark-runs/dispatch/r3/report.md#z-001) |
| dispatch | Какое состояние должно быть у ведомости после подтверждения перевозчика? | Полнота | 2/3 | [1/Z-002](benchmark-runs/dispatch/r1/report.md#z-002), [3/Z-002](benchmark-runs/dispatch/r3/report.md#z-002) |
| dispatch | Срок передачи черновика | Проверяемость | 3/3 | [1/Z-003](benchmark-runs/dispatch/r1/report.md#z-003), [2/Z-005](benchmark-runs/dispatch/r2/report.md#z-005), [3/Z-003](benchmark-runs/dispatch/r3/report.md#z-003) |
| dispatch | Разрешение отправки 25 строк | Противоречивость | 1/3 | [1/Z-004](benchmark-runs/dispatch/r1/report.md#z-004) |
| dispatch | Срок показа «Передано» | Проверяемость | 3/3 | [1/Z-005](benchmark-runs/dispatch/r1/report.md#z-005), [2/Z-003](benchmark-runs/dispatch/r2/report.md#z-003), [3/Z-005](benchmark-runs/dispatch/r3/report.md#z-005) |
| dispatch | Ссылка на отсутствующее правило S-97 | Трассируемость | 3/3 | [1/Z-007](benchmark-runs/dispatch/r1/report.md#z-007), [2/Z-006](benchmark-runs/dispatch/r2/report.md#z-006), [3/Z-007](benchmark-runs/dispatch/r3/report.md#z-007) |
| dispatch | Какие строки должны войти в ведомость, доступную для отправки после загрузки файла из 25 строк? | Полнота | 2/3 | [2/Z-002](benchmark-runs/dispatch/r2/report.md#z-002), [3/Z-004](benchmark-runs/dispatch/r3/report.md#z-004) |
| dispatch | Единица хранения подтверждения | Противоречивость | 1/3 | [3/Z-006](benchmark-runs/dispatch/r3/report.md#z-006) |
| dispatch-base | Интервал показа «Передано» | Однозначность | 3/3 | [1/Z-001](benchmark-runs/dispatch-base/r1/report.md#z-001), [2/Z-002](benchmark-runs/dispatch-base/r2/report.md#z-002), [3/Z-001](benchmark-runs/dispatch-base/r3/report.md#z-001) |
| dispatch-base | Какое состояние должна иметь ведомость после подтверждения перевозчика? Если она остаётся в состоянии «Готова», должна ли быть доступна повторная отправка той же ведомости? | Полнота | 1/3 | [2/Z-001](benchmark-runs/dispatch-base/r2/report.md#z-001) |
| irrigation | Какое действие ожидается при корректном показании влажности с учётом исходного состояния клапана, если ручная остановка не действует? | Полнота | 1/3 · спорное соответствие | [1/Z-001](benchmark-runs/irrigation/r1/report.md#z-001) |
| irrigation | Какое положение должен занять открытый клапан после нажатия кнопки ручной остановки, если новых команд открытия нет? | Полнота | 1/3 · спорное соответствие | [1/Z-003](benchmark-runs/irrigation/r1/report.md#z-003) |
| irrigation | Аварийный переход клапана | Полнота | 1/3 · спорное соответствие | [1/Z-008](benchmark-runs/irrigation/r1/report.md#z-008) |
| irrigation | Как корректные показания влажности влияют на клапан, если он закрыт, ручная остановка не активна и команд расписания нет? | Полнота | 1/3 · спорное соответствие | [2/Z-001](benchmark-runs/irrigation/r2/report.md#z-001) |
| irrigation | Условие и результат аварийного перехода | Полнота | 1/3 · спорное соответствие | [2/Z-002](benchmark-runs/irrigation/r2/report.md#z-002) |
| irrigation | Как должен отреагировать уже открытый клапан на нажатие кнопки ручной остановки, если новых команд открытия нет? | Полнота | 1/3 · спорное соответствие | [2/Z-004](benchmark-runs/irrigation/r2/report.md#z-004) |
| irrigation | Какое действие ожидается от контроллера при согласованном корректном показании и заданном исходном состоянии полива без ручной остановки? | Полнота | 1/3 · спорное соответствие | [3/Z-001](benchmark-runs/irrigation/r3/report.md#z-001) |
| irrigation | В каком состоянии должен оказаться открытый клапан после нажатия кнопки ручной остановки, если новых команд нет? | Полнота | 1/3 · спорное соответствие | [3/Z-003](benchmark-runs/irrigation/r3/report.md#z-003) |
| irrigation | Аварийное положение клапана | Полнота | 1/3 · спорное соответствие | [3/Z-007](benchmark-runs/irrigation/r3/report.md#z-007) |
| irrigation | По каким признакам полученное показание считается некорректным для W-4? | Полнота | 1/3 · спорное соответствие | [3/Z-008](benchmark-runs/irrigation/r3/report.md#z-008) |
| irrigation | Какое значение должна получить панель и из каких исходных данных его определить для приёмки? | Полнота | 3/3 | [1/Z-002](benchmark-runs/irrigation/r1/report.md#z-002), [2/Z-003](benchmark-runs/irrigation/r2/report.md#z-003), [3/Z-002](benchmark-runs/irrigation/r3/report.md#z-002) |
| irrigation | Команда расписания при ручной остановке | Противоречивость | 3/3 | [1/Z-004](benchmark-runs/irrigation/r1/report.md#z-004), [2/Z-005](benchmark-runs/irrigation/r2/report.md#z-005), [3/Z-004](benchmark-runs/irrigation/r3/report.md#z-004) |
| irrigation | Критерий немедленного открытия | Проверяемость | 1/3 · спорное соответствие | [1/Z-005](benchmark-runs/irrigation/r1/report.md#z-005) |
| irrigation | Обязательная проверка кнопки «Возобновить» | Проверяемость | 1/3 · спорное соответствие | [1/Z-006](benchmark-runs/irrigation/r1/report.md#z-006) |
| irrigation | Приёмка проверки кнопки «Возобновить» | Проверяемость | 1/3 · спорное соответствие | [2/Z-006](benchmark-runs/irrigation/r2/report.md#z-006) |
| irrigation | Задержка открытия по расписанию | Проверяемость | 1/3 · спорное соответствие | [2/Z-009](benchmark-runs/irrigation/r2/report.md#z-009) |
| irrigation | Проверка кнопки «Возобновить» | Проверяемость | 1/3 · спорное соответствие | [3/Z-005](benchmark-runs/irrigation/r3/report.md#z-005) |
| irrigation | Время открытия по расписанию | Проверяемость | 1/3 · спорное соответствие | [3/Z-010](benchmark-runs/irrigation/r3/report.md#z-010) |
| irrigation | Категория омега | Ясность | 3/3 | [1/Z-007](benchmark-runs/irrigation/r1/report.md#z-007), [2/Z-007](benchmark-runs/irrigation/r2/report.md#z-007), [3/Z-006](benchmark-runs/irrigation/r3/report.md#z-006) |
| irrigation | Число повторов после таймаута | Противоречивость | 3/3 | [1/Z-009](benchmark-runs/irrigation/r1/report.md#z-009), [2/Z-008](benchmark-runs/irrigation/r2/report.md#z-008), [3/Z-009](benchmark-runs/irrigation/r3/report.md#z-009) |
| irrigation-base | Как должен реагировать клапан на корректное показание влажности при выбранной зоне и снятой ручной остановке? | Полнота | 1/3 · спорное соответствие | [1/Z-001](benchmark-runs/irrigation-base/r1/report.md#z-001) |
| irrigation-base | Как должен отреагировать уже открытый клапан на нажатие кнопки ручной остановки, если новых команд нет? | Полнота | 1/3 · спорное соответствие | [1/Z-003](benchmark-runs/irrigation-base/r1/report.md#z-003) |
| irrigation-base | Должно ли корректное показание влажности само влиять на клапан при выбранной зоне, выключенной ручной остановке и отсутствии команды расписания? Если да, при каких показаниях и каким образом? | Полнота | 1/3 · спорное соответствие | [2/Z-001](benchmark-runs/irrigation-base/r2/report.md#z-001) |
| irrigation-base | В каком положении должен быть открытый клапан после нажатия кнопки ручной остановки во время полива, если других событий не поступило? | Полнота | 1/3 · спорное соответствие | [2/Z-004](benchmark-runs/irrigation-base/r2/report.md#z-004) |
| irrigation-base | Как контроллер должен управлять клапаном по корректным показаниям влажности при выбранной зоне и снятой ручной остановке? | Полнота | 1/3 · спорное соответствие | [3/Z-001](benchmark-runs/irrigation-base/r3/report.md#z-001) |
| irrigation-base | Какое положение должен занять уже открытый клапан при нажатии кнопки ручной остановки без новых команд открытия? | Полнота | 1/3 · спорное соответствие | [3/Z-004](benchmark-runs/irrigation-base/r3/report.md#z-004) |
| irrigation-base | Какое значение передаётся панели и откуда контроллер его получает? | Полнота | 3/3 | [1/Z-002](benchmark-runs/irrigation-base/r1/report.md#z-002), [2/Z-002](benchmark-runs/irrigation-base/r2/report.md#z-002), [3/Z-002](benchmark-runs/irrigation-base/r3/report.md#z-002) |
| irrigation-base | Входит ли в проверку возобновления случай, когда обработка очередной команды открытия пересекается с обработкой некорректного показания? Если входит, какая последовательность положений клапана ожидается? | Полнота | 2/3 | [1/Z-004](benchmark-runs/irrigation-base/r1/report.md#z-004), [3/Z-005](benchmark-runs/irrigation-base/r3/report.md#z-005) |
| irrigation-base | Критерий некорректного показания | Проверяемость | 3/3 | [1/Z-005](benchmark-runs/irrigation-base/r1/report.md#z-005), [2/Z-003](benchmark-runs/irrigation-base/r2/report.md#z-003), [3/Z-003](benchmark-runs/irrigation-base/r3/report.md#z-003) |
| irrigation-base | Дублирование числа повторов | Дублирование | 1/3 | [1/Z-006](benchmark-runs/irrigation-base/r1/report.md#z-006) |
| subtitles | Критерий лёгкости экспорта | Проверяемость | 3/3 | [1/Z-001](benchmark-runs/subtitles/r1/report.md#z-001), [2/Z-003](benchmark-runs/subtitles/r2/report.md#z-003), [3/Z-003](benchmark-runs/subtitles/r3/report.md#z-003) |
| subtitles | BOM при экспорте | Противоречивость | 3/3 | [1/Z-002](benchmark-runs/subtitles/r1/report.md#z-002), [2/Z-001](benchmark-runs/subtitles/r2/report.md#z-001), [3/Z-001](benchmark-runs/subtitles/r3/report.md#z-001) |
| subtitles | Шкала временных меток | Противоречивость | 1/3 | [1/Z-003](benchmark-runs/subtitles/r1/report.md#z-003) |
| subtitles | Реплика из 81 кодовой точки | Противоречивость | 3/3 | [1/Z-004](benchmark-runs/subtitles/r1/report.md#z-004), [2/Z-004](benchmark-runs/subtitles/r2/report.md#z-004), [3/Z-004](benchmark-runs/subtitles/r3/report.md#z-004) |
| subtitles | Ссылка на сообщение пустой дорожки | Трассируемость | 3/3 | [1/Z-005](benchmark-runs/subtitles/r1/report.md#z-005), [2/Z-005](benchmark-runs/subtitles/r2/report.md#z-005), [3/Z-005](benchmark-runs/subtitles/r3/report.md#z-005) |
| subtitles | В T-3 миллисекунды относятся к числу, записанному в поле, или к длительности после его преобразования? | Полнота | 1/3 | [3/Z-002](benchmark-runs/subtitles/r3/report.md#z-002) |
| subtitles-base | Где потребитель экспортного формата может проверить объявление миллисекунд для каждого поля временной метки? | Полнота | 1/3 | [1/Z-002](benchmark-runs/subtitles-base/r1/report.md#z-002) |
| subtitles-base | Как наблюдать отклонение реплики из 81 кодовой точки при экспорте дорожки из 100 реплик на ST-1 и какой результат ожидается для остальных реплик, файла назначения и диалога завершения? | Полнота | 1/3 · спорное соответствие | [1/Z-003](benchmark-runs/subtitles-base/r1/report.md#z-003) |
| subtitles-base | Какой результат экспорта ожидается для непустой дорожки с одной допустимой репликой и одной репликой из 81 кодовой точки, если файла назначения ещё нет? | Полнота | 1/3 · спорное соответствие | [2/Z-001](benchmark-runs/subtitles-base/r2/report.md#z-001) |
| subtitles-base | Каков ожидаемый результат экспорта в новый файл, если одна реплика допустима, а другая превышает лимит длины? | Полнота | 1/3 · спорное соответствие | [3/Z-001](benchmark-runs/subtitles-base/r3/report.md#z-001) |
| subtitles-base | Как идентифицировать рабочую станцию ST-1 для приёмочного замера? | Полнота | 1/3 · спорное соответствие | [3/Z-003](benchmark-runs/subtitles-base/r3/report.md#z-003) |
| subtitles-base | Обозначение единицы в поле временной метки | Однозначность | 2/3 | [2/Z-002](benchmark-runs/subtitles-base/r2/report.md#z-002), [3/Z-002](benchmark-runs/subtitles-base/r3/report.md#z-002) |
