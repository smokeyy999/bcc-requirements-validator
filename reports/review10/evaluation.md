# Качество на размеченном корпусе

Дата оценки 2026-11-27T11:20:21+05:00. Провайдер и модель — OpenAI через Codex CLI · gpt-6.2-sol. Коммит реализации — `7db8d3d2b878bcb26fad0412b5ea70bef9651f5f`.

Основной результат измерен по первому запуску каждого документа. Полнота — **15/15 (100.0%)**. Точность — **15/27 (55.6%)**.

Во всех 3 прогонах воспроизвелось **23/34 (67.6%)** групп замечаний.

## Метод

Разметка и базовые версии не включаются в запросы модели. Балл даётся за точную категорию и пересечение цитат со всеми раздельно заданными диапазонами дефекта. Только одна пара «замечание — дефект» может получить балл. Конкурирующие пары и совпадения лишь по строкам остаются незачтёнными. Требования к совпадению зафиксированы до измерения. В знаменатель точности входят все опубликованные карточки Z, включая вопросы и рекомендации. Существование других реальных дефектов, включая контрольные документы, возможно. [Незачтённые замечания для проверки человеком](evaluation-manual.md)

Результаты dev и test приведены отдельно. Dev служит для разработки. Разметка test предназначена для измерения после фиксации механизма и не должна применяться для подбора подсказок.

| Часть | Прогон | Полнота | Точность |
|---|---:|---:|---:|
| all | 1 | 15/15 (100.0%) | 15/27 (55.6%) |
| all | 2 | 15/15 (100.0%) | 15/27 (55.6%) |
| all | 3 | 15/15 (100.0%) | 15/27 (55.6%) |
| dev | 1 | 5/5 (100.0%) | 5/7 (71.4%) |
| dev | 2 | 5/5 (100.0%) | 5/6 (83.3%) |
| dev | 3 | 5/5 (100.0%) | 5/7 (71.4%) |
| test | 1 | 10/10 (100.0%) | 10/20 (50.0%) |
| test | 2 | 10/10 (100.0%) | 10/21 (47.6%) |
| test | 3 | 10/10 (100.0%) | 10/20 (50.0%) |

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
| несовпадение единиц | 1 | 2/2 (100.0%) |
| несовпадение единиц | 2 | 2/2 (100.0%) |
| несовпадение единиц | 3 | 2/2 (100.0%) |
| отсутствие критерия приёмки | 1 | 1/1 (100.0%) |
| отсутствие критерия приёмки | 2 | 1/1 (100.0%) |
| отсутствие критерия приёмки | 3 | 1/1 (100.0%) |
| отсутствие обработки ошибки | 1 | 1/1 (100.0%) |
| отсутствие обработки ошибки | 2 | 1/1 (100.0%) |
| отсутствие обработки ошибки | 3 | 1/1 (100.0%) |
| противоречие между правилами | 1 | 3/3 (100.0%) |
| противоречие между правилами | 2 | 3/3 (100.0%) |
| противоречие между правилами | 3 | 3/3 (100.0%) |
| разные числа для одного параметра | 1 | 2/2 (100.0%) |
| разные числа для одного параметра | 2 | 2/2 (100.0%) |
| разные числа для одного параметра | 3 | 2/2 (100.0%) |
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
| dispatch / dev | D-02 | разные числа для одного параметра | Противоречивость | 10, 11 | Файл из 25 строк принят при максимуме 24. | [Z-002](benchmark-runs/dispatch/r1/report.md#z-002) · [Z-003](benchmark-runs/dispatch/r2/report.md#z-003) · [Z-002](benchmark-runs/dispatch/r3/report.md#z-002) |
| dispatch / dev | D-03 | расплывчатый срок | Проверяемость | 12 | «Достаточно быстро» не задаёт предела для отображения результата. | [Z-003](benchmark-runs/dispatch/r1/report.md#z-003) · [Z-004](benchmark-runs/dispatch/r2/report.md#z-004) · [Z-003](benchmark-runs/dispatch/r3/report.md#z-003) |
| dispatch / dev | D-04 | ссылка на несуществующий ID | Трассируемость | 13 | Для сообщения об отказе указана отсутствующая норма S-97. | [Z-006](benchmark-runs/dispatch/r1/report.md#z-006) · [Z-006](benchmark-runs/dispatch/r2/report.md#z-006) · [Z-006](benchmark-runs/dispatch/r3/report.md#z-006) |
| dispatch / dev | D-05 | несовпадение единиц | Противоречивость | 15 | Один параметр измеряется в сутках, но его значение интерпретируется как часы. | [Z-004](benchmark-runs/dispatch/r1/report.md#z-004) · [Z-005](benchmark-runs/dispatch/r2/report.md#z-005) · [Z-004](benchmark-runs/dispatch/r3/report.md#z-004) |
| irrigation / test | I-01 | противоречие между правилами | Противоречивость | 6, 7 | Автоматика одновременно игнорирует команду и открывает клапан при ручной остановке. | [Z-004](benchmark-runs/irrigation/r1/report.md#z-004) · [Z-005](benchmark-runs/irrigation/r2/report.md#z-005) · [Z-004](benchmark-runs/irrigation/r3/report.md#z-004) |
| irrigation / test | I-02 | неопределённый термин | Ясность | 8 | Не определены признаки зоны категории омега. | [Z-006](benchmark-runs/irrigation/r1/report.md#z-006) · [Z-007](benchmark-runs/irrigation/r2/report.md#z-007) · [Z-006](benchmark-runs/irrigation/r3/report.md#z-006) |
| irrigation / test | I-03 | отсутствие обработки ошибки | Полнота | 9 | Документ требует аварийного положения клапана, но убрано указание, какое положение выбрать при некорректном датчике. | [Z-007](benchmark-runs/irrigation/r1/report.md#z-007) · [Z-008](benchmark-runs/irrigation/r2/report.md#z-008) · [Z-007](benchmark-runs/irrigation/r3/report.md#z-007) |
| irrigation / test | I-04 | отсутствие критерия приёмки | Полнота | 10 | Обязательному испытанию кнопки не заданы шаг и ожидаемый результат. | [Z-005](benchmark-runs/irrigation/r1/report.md#z-005) · [Z-006](benchmark-runs/irrigation/r2/report.md#z-006) · [Z-005](benchmark-runs/irrigation/r3/report.md#z-005) |
| irrigation / test | I-05 | дублирование с разными значениями | Противоречивость | 13, 14 | Для одной и той же повторной передачи предписаны три и пять повторов. | [Z-008](benchmark-runs/irrigation/r1/report.md#z-008) · [Z-009](benchmark-runs/irrigation/r2/report.md#z-009) · [Z-008](benchmark-runs/irrigation/r3/report.md#z-008) |
| subtitles / test | S-01 | противоречие между правилами | Противоречивость | 6, 7 | Маркер BOM одновременно обязателен и запрещён. | [Z-001](benchmark-runs/subtitles/r1/report.md#z-001) · [Z-002](benchmark-runs/subtitles/r2/report.md#z-002) · [Z-001](benchmark-runs/subtitles/r3/report.md#z-001) |
| subtitles / test | S-02 | несовпадение единиц | Противоречивость | 8 | 1000 мс названы одной минутой. | [Z-002](benchmark-runs/subtitles/r1/report.md#z-002) · [Z-003](benchmark-runs/subtitles/r2/report.md#z-003) · [Z-002](benchmark-runs/subtitles/r3/report.md#z-002) |
| subtitles / test | S-03 | непроверяемое нефункциональное требование | Проверяемость | 9 | Нет объективного способа принять «effortless to every user». | [Z-003](benchmark-runs/subtitles/r1/report.md#z-003) · [Z-001](benchmark-runs/subtitles/r2/report.md#z-001) · [Z-003](benchmark-runs/subtitles/r3/report.md#z-003) |
| subtitles / test | S-04 | ссылка на несуществующий ID | Трассируемость | 10 | Указан отсутствующий T-40 вместо существующего описания сообщения. | [Z-005](benchmark-runs/subtitles/r1/report.md#z-005) · [Z-005](benchmark-runs/subtitles/r2/report.md#z-005) · [Z-005](benchmark-runs/subtitles/r3/report.md#z-005) |
| subtitles / test | S-05 | разные числа для одного параметра | Противоречивость | 14, 15 | Тест принимает длину 81 при предельной длине 80. | [Z-004](benchmark-runs/subtitles/r1/report.md#z-004) · [Z-004](benchmark-runs/subtitles/r2/report.md#z-004) · [Z-004](benchmark-runs/subtitles/r3/report.md#z-004) |

## Сохранённые отчёты и контрольные документы

| Отчёт и прогон | Часть | Заложено | Замечаний | Зачтено |
|---|---|---:|---:|---:|
| [dispatch · 1](benchmark-runs/dispatch/r1/report.md) | dev | 5 | 5 | 5 |
| [dispatch · 2](benchmark-runs/dispatch/r2/report.md) | dev | 5 | 5 | 5 |
| [dispatch · 3](benchmark-runs/dispatch/r3/report.md) | dev | 5 | 6 | 5 |
| [dispatch-base · 1](benchmark-runs/dispatch-base/r1/report.md) | dev | 0 | 2 | 0 |
| [dispatch-base · 2](benchmark-runs/dispatch-base/r2/report.md) | dev | 0 | 1 | 0 |
| [dispatch-base · 3](benchmark-runs/dispatch-base/r3/report.md) | dev | 0 | 1 | 0 |
| [indicator · 1](benchmark-runs/indicator/r1/report.md) | test | 0 | 0 | 0 |
| [indicator · 2](benchmark-runs/indicator/r2/report.md) | test | 0 | 0 | 0 |
| [indicator · 3](benchmark-runs/indicator/r3/report.md) | test | 0 | 0 | 0 |
| [irrigation · 1](benchmark-runs/irrigation/r1/report.md) | test | 5 | 8 | 5 |
| [irrigation · 2](benchmark-runs/irrigation/r2/report.md) | test | 5 | 8 | 5 |
| [irrigation · 3](benchmark-runs/irrigation/r3/report.md) | test | 5 | 8 | 5 |
| [irrigation-base · 1](benchmark-runs/irrigation-base/r1/report.md) | test | 0 | 5 | 0 |
| [irrigation-base · 2](benchmark-runs/irrigation-base/r2/report.md) | test | 0 | 5 | 0 |
| [irrigation-base · 3](benchmark-runs/irrigation-base/r3/report.md) | test | 0 | 5 | 0 |
| [subtitles · 1](benchmark-runs/subtitles/r1/report.md) | test | 5 | 5 | 5 |
| [subtitles · 2](benchmark-runs/subtitles/r2/report.md) | test | 5 | 5 | 5 |
| [subtitles · 3](benchmark-runs/subtitles/r3/report.md) | test | 5 | 5 | 5 |
| [subtitles-base · 1](benchmark-runs/subtitles-base/r1/report.md) | test | 0 | 2 | 0 |
| [subtitles-base · 2](benchmark-runs/subtitles-base/r2/report.md) | test | 0 | 3 | 0 |
| [subtitles-base · 3](benchmark-runs/subtitles-base/r3/report.md) | test | 0 | 2 | 0 |

## Воспроизводимость замечаний

В одном документе сравниваются независимо полученные находки одной категории, у которых есть общая строка доказательства во всех вошедших прогонах и не более одного замечания в каждом. Конкурирующие или транзитивные совпадения показаны по отдельности и не дают балла устойчивости.

| ТЗ | Замечание | Категория | Частота | Прогон и ID |
|---|---|---|---:|---|
| dispatch | Отправка черновика | Противоречивость | 3/3 | [1/Z-001](benchmark-runs/dispatch/r1/report.md#z-001), [2/Z-001](benchmark-runs/dispatch/r2/report.md#z-001), [3/Z-001](benchmark-runs/dispatch/r3/report.md#z-001) |
| dispatch | Отправка ведомости из 25 строк | Противоречивость | 3/3 | [1/Z-002](benchmark-runs/dispatch/r1/report.md#z-002), [2/Z-003](benchmark-runs/dispatch/r2/report.md#z-003), [3/Z-002](benchmark-runs/dispatch/r3/report.md#z-002) |
| dispatch | Задержка сообщения «Передано» | Проверяемость | 3/3 | [1/Z-003](benchmark-runs/dispatch/r1/report.md#z-003), [2/Z-004](benchmark-runs/dispatch/r2/report.md#z-004), [3/Z-003](benchmark-runs/dispatch/r3/report.md#z-003) |
| dispatch | Срок хранения при значении 7 | Противоречивость | 3/3 | [1/Z-004](benchmark-runs/dispatch/r1/report.md#z-004), [2/Z-005](benchmark-runs/dispatch/r2/report.md#z-005), [3/Z-004](benchmark-runs/dispatch/r3/report.md#z-004) |
| dispatch | Отсутствует цель внутренней ссылки S-97 | Трассируемость | 3/3 | [1/Z-006](benchmark-runs/dispatch/r1/report.md#z-006), [2/Z-006](benchmark-runs/dispatch/r2/report.md#z-006), [3/Z-006](benchmark-runs/dispatch/r3/report.md#z-006) |
| dispatch | Если передачу черновика сохранят, какая максимальная задержка от попытки отправки до передачи ведомости перевозчику допустима? | Проверяемость | 1/3 | [3/Z-005](benchmark-runs/dispatch/r3/report.md#z-005) |
| dispatch-base | В каком состоянии должна быть та же ведомость после подтверждения перевозчика? | Полнота | 1/3 | [1/Z-001](benchmark-runs/dispatch-base/r1/report.md#z-001) |
| dispatch-base | Три секунды после подтверждения | Однозначность | 3/3 | [1/Z-003](benchmark-runs/dispatch-base/r1/report.md#z-003), [2/Z-001](benchmark-runs/dispatch-base/r2/report.md#z-001), [3/Z-001](benchmark-runs/dispatch-base/r3/report.md#z-001) |
| irrigation | Как должен отреагировать контроллер на допустимое показание влажности при закрытом клапане, если ручная остановка не активна и команды расписания нет? | Полнота | 3/3 | [1/Z-001](benchmark-runs/irrigation/r1/report.md#z-001), [2/Z-001](benchmark-runs/irrigation/r2/report.md#z-001), [3/Z-002](benchmark-runs/irrigation/r3/report.md#z-002) |
| irrigation | По какому критерию числовое показание датчика считается некорректным для применения W-4? | Ясность | 3/3 | [1/Z-002](benchmark-runs/irrigation/r1/report.md#z-002), [2/Z-002](benchmark-runs/irrigation/r2/report.md#z-002), [3/Z-001](benchmark-runs/irrigation/r3/report.md#z-001) |
| irrigation | Из какого источника контроллер берёт значение, которое передаёт панели и повторно отправляет после первого таймаута? | Трассируемость | 3/3 | [1/Z-003](benchmark-runs/irrigation/r1/report.md#z-003), [2/Z-003](benchmark-runs/irrigation/r2/report.md#z-003), [3/Z-003](benchmark-runs/irrigation/r3/report.md#z-003) |
| irrigation | Открытие по расписанию при ручной остановке | Противоречивость | 3/3 | [1/Z-004](benchmark-runs/irrigation/r1/report.md#z-004), [2/Z-005](benchmark-runs/irrigation/r2/report.md#z-005), [3/Z-004](benchmark-runs/irrigation/r3/report.md#z-004) |
| irrigation | Приёмочное испытание кнопки «Возобновить» | Полнота | 3/3 | [1/Z-005](benchmark-runs/irrigation/r1/report.md#z-005), [2/Z-006](benchmark-runs/irrigation/r2/report.md#z-006), [3/Z-005](benchmark-runs/irrigation/r3/report.md#z-005) |
| irrigation | Как определить, относится ли конкретная зона к категории омега по W-3? | Ясность | 3/3 | [1/Z-006](benchmark-runs/irrigation/r1/report.md#z-006), [2/Z-007](benchmark-runs/irrigation/r2/report.md#z-007), [3/Z-006](benchmark-runs/irrigation/r3/report.md#z-006) |
| irrigation | Конечное аварийное положение клапана | Полнота | 3/3 | [1/Z-007](benchmark-runs/irrigation/r1/report.md#z-007), [2/Z-008](benchmark-runs/irrigation/r2/report.md#z-008), [3/Z-007](benchmark-runs/irrigation/r3/report.md#z-007) |
| irrigation | Число повторных передач после таймаута | Противоречивость | 3/3 | [1/Z-008](benchmark-runs/irrigation/r1/report.md#z-008), [2/Z-009](benchmark-runs/irrigation/r2/report.md#z-009), [3/Z-008](benchmark-runs/irrigation/r3/report.md#z-008) |
| irrigation-base | Как по корректному показанию влажности определить, должен ли контроллер открыть закрытый клапан при работающей автоматике и снятой ручной остановке? | Полнота | 1/3 · спорное соответствие | [1/Z-001](benchmark-runs/irrigation-base/r1/report.md#z-001) |
| irrigation-base | Должно ли нажатие кнопки ручной остановки закрыть уже открытый клапан, если других команд нет? | Полнота | 1/3 · спорное соответствие | [1/Z-003](benchmark-runs/irrigation-base/r1/report.md#z-003) |
| irrigation-base | Действие при корректной влажности | Полнота | 1/3 · спорное соответствие | [2/Z-002](benchmark-runs/irrigation-base/r2/report.md#z-002) |
| irrigation-base | В каком состоянии должен быть уже открытый клапан сразу после ручной остановки, если новых команд открытия ещё не было? | Полнота | 1/3 · спорное соответствие | [2/Z-003](benchmark-runs/irrigation-base/r2/report.md#z-003) |
| irrigation-base | Каким должно быть положение уже открытого клапана после получения согласованного корректного показания при выбранной зоне, вне ручной остановки и без команды расписания? | Полнота | 1/3 · спорное соответствие | [3/Z-001](benchmark-runs/irrigation-base/r3/report.md#z-001) |
| irrigation-base | Каким должно быть положение уже открытого клапана после нажатия кнопки ручной остановки, если новых команд нет? | Полнота | 1/3 · спорное соответствие | [3/Z-004](benchmark-runs/irrigation-base/r3/report.md#z-004) |
| irrigation-base | Из какого входа или состояния контроллера берётся значение, передаваемое панели? | Трассируемость | 3/3 | [1/Z-002](benchmark-runs/irrigation-base/r1/report.md#z-002), [2/Z-001](benchmark-runs/irrigation-base/r2/report.md#z-001), [3/Z-003](benchmark-runs/irrigation-base/r3/report.md#z-003) |
| irrigation-base | По какому критерию показание датчика относится к некорректным для применения W-4? | Ясность | 3/3 | [1/Z-004](benchmark-runs/irrigation-base/r1/report.md#z-004), [2/Z-004](benchmark-runs/irrigation-base/r2/report.md#z-004), [3/Z-002](benchmark-runs/irrigation-base/r3/report.md#z-002) |
| irrigation-base | Дубль требования о трёх повторах | Дублирование | 3/3 | [1/Z-005](benchmark-runs/irrigation-base/r1/report.md#z-005), [2/Z-005](benchmark-runs/irrigation-base/r2/report.md#z-005), [3/Z-005](benchmark-runs/irrigation-base/r3/report.md#z-005) |
| subtitles | BOM в файле экспорта | Противоречивость | 3/3 | [1/Z-001](benchmark-runs/subtitles/r1/report.md#z-001), [2/Z-002](benchmark-runs/subtitles/r2/report.md#z-002), [3/Z-001](benchmark-runs/subtitles/r3/report.md#z-001) |
| subtitles | Шкала временных отметок | Противоречивость | 3/3 | [1/Z-002](benchmark-runs/subtitles/r1/report.md#z-002), [2/Z-003](benchmark-runs/subtitles/r2/report.md#z-003), [3/Z-002](benchmark-runs/subtitles/r3/report.md#z-002) |
| subtitles | Критерий удобства экспорта | Проверяемость | 3/3 | [1/Z-003](benchmark-runs/subtitles/r1/report.md#z-003), [2/Z-001](benchmark-runs/subtitles/r2/report.md#z-001), [3/Z-003](benchmark-runs/subtitles/r3/report.md#z-003) |
| subtitles | Приёмка реплики из 81 кодовой точки | Противоречивость | 3/3 | [1/Z-004](benchmark-runs/subtitles/r1/report.md#z-004), [2/Z-004](benchmark-runs/subtitles/r2/report.md#z-004), [3/Z-004](benchmark-runs/subtitles/r3/report.md#z-004) |
| subtitles | Отсутствует цель внутренней ссылки T-40 | Трассируемость | 3/3 | [1/Z-005](benchmark-runs/subtitles/r1/report.md#z-005), [2/Z-005](benchmark-runs/subtitles/r2/report.md#z-005), [3/Z-005](benchmark-runs/subtitles/r3/report.md#z-005) |
| subtitles-base | Какое наблюдаемое представление считается объявлением миллисекунд для каждого поля временной метки? | Проверяемость | 1/3 | [1/Z-002](benchmark-runs/subtitles-base/r1/report.md#z-002) |
| subtitles-base | Каким должно быть состояние существующего файла назначения после экспорта дорожки с репликами из 80 и 81 кодовой точки при обязательном отклонении второй реплики? | Полнота | 3/3 | [1/Z-003](benchmark-runs/subtitles-base/r1/report.md#z-003), [2/Z-001](benchmark-runs/subtitles-base/r2/report.md#z-001), [3/Z-001](benchmark-runs/subtitles-base/r3/report.md#z-001) |
| subtitles-base | В каком месте и в какой форме должно быть представлено обязательное объявление миллисекунд для каждого поля временной метки? | Полнота | 2/3 | [2/Z-002](benchmark-runs/subtitles-base/r2/report.md#z-002), [3/Z-002](benchmark-runs/subtitles-base/r3/report.md#z-002) |
| subtitles-base | Какая рабочая станция соответствует обозначению ST-1 в T-4 и по какому идентификатору её найти? | Трассируемость | 1/3 | [2/Z-003](benchmark-runs/subtitles-base/r2/report.md#z-003) |
