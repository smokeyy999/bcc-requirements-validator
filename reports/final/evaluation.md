# Качество на размеченном корпусе

Дата оценки 2026-11-26T23:10:29+05:00. Провайдер и модель — OpenAI через Codex CLI · gpt-6.2-sol. Коммит реализации — `bf920eba9f573a9872e4a2663c28e363b0f59881`.

Основной результат измерен по первому запуску каждого документа. Полнота — **13/15 (86.7%)**. Точность — **13/28 (46.4%)**.

Во всех 3 прогонах воспроизвелось **17/56 (30.4%)** групп замечаний.

## Метод

Разметка и базовые версии не включаются в запросы модели. Балл даётся за точную категорию и пересечение цитат со всеми раздельно заданными диапазонами дефекта. Только одна пара «замечание — дефект» может получить балл. Конкурирующие пары и совпадения лишь по строкам остаются незачтёнными. Требования к совпадению зафиксированы до измерения. В знаменатель точности входят все опубликованные карточки Z, включая вопросы и рекомендации. Существование других реальных дефектов, включая контрольные документы, возможно. [Незачтённые замечания для проверки человеком](evaluation-manual.md)

Результаты dev и test приведены отдельно. Dev служит для разработки. Разметка test предназначена для измерения после фиксации механизма и не должна применяться для подбора подсказок.

| Часть | Прогон | Полнота | Точность |
|---|---:|---:|---:|
| all | 1 | 13/15 (86.7%) | 13/28 (46.4%) |
| all | 2 | 12/15 (80.0%) | 12/32 (37.5%) |
| all | 3 | 12/15 (80.0%) | 12/34 (35.3%) |
| dev | 1 | 4/5 (80.0%) | 4/6 (66.7%) |
| dev | 2 | 4/5 (80.0%) | 4/8 (50.0%) |
| dev | 3 | 5/5 (100.0%) | 5/10 (50.0%) |
| test | 1 | 9/10 (90.0%) | 9/22 (40.9%) |
| test | 2 | 8/10 (80.0%) | 8/24 (33.3%) |
| test | 3 | 7/10 (70.0%) | 7/24 (29.2%) |

## Типы дефектов

| Тип | Прогон | Найдено / заложено |
|---|---:|---:|
| дублирование с разными значениями | 1 | 1/1 (100.0%) |
| дублирование с разными значениями | 2 | 1/1 (100.0%) |
| дублирование с разными значениями | 3 | 1/1 (100.0%) |
| неопределённый термин | 1 | 1/1 (100.0%) |
| неопределённый термин | 2 | 0/1 (0.0%) |
| неопределённый термин | 3 | 0/1 (0.0%) |
| непроверяемое нефункциональное требование | 1 | 1/1 (100.0%) |
| непроверяемое нефункциональное требование | 2 | 1/1 (100.0%) |
| непроверяемое нефункциональное требование | 3 | 1/1 (100.0%) |
| несовпадение единиц | 1 | 1/2 (50.0%) |
| несовпадение единиц | 2 | 1/2 (50.0%) |
| несовпадение единиц | 3 | 2/2 (100.0%) |
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
| dispatch / dev | D-02 | разные числа для одного параметра | Противоречивость | 10, 11 | Файл из 25 строк принят при максимуме 24. | [Z-004](benchmark-runs/dispatch/r1/report.md#z-004) · [Z-002](benchmark-runs/dispatch/r2/report.md#z-002) · [Z-002](benchmark-runs/dispatch/r3/report.md#z-002) |
| dispatch / dev | D-03 | расплывчатый срок | Проверяемость | 12 | «Достаточно быстро» не задаёт предела для отображения результата. | [Z-005](benchmark-runs/dispatch/r1/report.md#z-005) · [Z-004](benchmark-runs/dispatch/r2/report.md#z-004) · [Z-004](benchmark-runs/dispatch/r3/report.md#z-004) |
| dispatch / dev | D-04 | ссылка на несуществующий ID | Трассируемость | 13 | Для сообщения об отказе указана отсутствующая норма S-97. | [Z-006](benchmark-runs/dispatch/r1/report.md#z-006) · [Z-006](benchmark-runs/dispatch/r2/report.md#z-006) · [Z-007](benchmark-runs/dispatch/r3/report.md#z-007) |
| dispatch / dev | D-05 | несовпадение единиц | Противоречивость | 15 | Один параметр измеряется в сутках, но его значение интерпретируется как часы. | пропуск · пропуск · [Z-005](benchmark-runs/dispatch/r3/report.md#z-005) |
| irrigation / test | I-01 | противоречие между правилами | Противоречивость | 6, 7 | Автоматика одновременно игнорирует команду и открывает клапан при ручной остановке. | [Z-004](benchmark-runs/irrigation/r1/report.md#z-004) · [Z-005](benchmark-runs/irrigation/r2/report.md#z-005) · [Z-005](benchmark-runs/irrigation/r3/report.md#z-005) |
| irrigation / test | I-02 | неопределённый термин | Ясность | 8 | Не определены признаки зоны категории омега. | [Z-007](benchmark-runs/irrigation/r1/report.md#z-007) · пропуск · пропуск |
| irrigation / test | I-03 | отсутствие обработки ошибки | Полнота | 9 | Документ требует аварийного положения клапана, но убрано указание, какое положение выбрать при некорректном датчике. | [Z-008](benchmark-runs/irrigation/r1/report.md#z-008) · [Z-001](benchmark-runs/irrigation/r2/report.md#z-001) · пропуск |
| irrigation / test | I-04 | отсутствие критерия приёмки | Полнота | 10 | Обязательному испытанию кнопки не заданы шаг и ожидаемый результат. | пропуск · пропуск · пропуск |
| irrigation / test | I-05 | дублирование с разными значениями | Противоречивость | 13, 14 | Для одной и той же повторной передачи предписаны три и пять повторов. | [Z-009](benchmark-runs/irrigation/r1/report.md#z-009) · [Z-009](benchmark-runs/irrigation/r2/report.md#z-009) · [Z-009](benchmark-runs/irrigation/r3/report.md#z-009) |
| subtitles / test | S-01 | противоречие между правилами | Противоречивость | 6, 7 | Маркер BOM одновременно обязателен и запрещён. | [Z-002](benchmark-runs/subtitles/r1/report.md#z-002) · [Z-002](benchmark-runs/subtitles/r2/report.md#z-002) · [Z-001](benchmark-runs/subtitles/r3/report.md#z-001) |
| subtitles / test | S-02 | несовпадение единиц | Противоречивость | 8 | 1000 мс названы одной минутой. | [Z-003](benchmark-runs/subtitles/r1/report.md#z-003) · [Z-003](benchmark-runs/subtitles/r2/report.md#z-003) · [Z-002](benchmark-runs/subtitles/r3/report.md#z-002) |
| subtitles / test | S-03 | непроверяемое нефункциональное требование | Проверяемость | 9 | Нет объективного способа принять «effortless to every user». | [Z-004](benchmark-runs/subtitles/r1/report.md#z-004) · [Z-004](benchmark-runs/subtitles/r2/report.md#z-004) · [Z-003](benchmark-runs/subtitles/r3/report.md#z-003) |
| subtitles / test | S-04 | ссылка на несуществующий ID | Трассируемость | 10 | Указан отсутствующий T-40 вместо существующего описания сообщения. | [Z-006](benchmark-runs/subtitles/r1/report.md#z-006) · [Z-006](benchmark-runs/subtitles/r2/report.md#z-006) · [Z-004](benchmark-runs/subtitles/r3/report.md#z-004) |
| subtitles / test | S-05 | разные числа для одного параметра | Противоречивость | 14, 15 | Тест принимает длину 81 при предельной длине 80. | [Z-005](benchmark-runs/subtitles/r1/report.md#z-005) · [Z-005](benchmark-runs/subtitles/r2/report.md#z-005) · [Z-005](benchmark-runs/subtitles/r3/report.md#z-005) |

## Сохранённые отчёты и контрольные документы

| Отчёт и прогон | Часть | Заложено | Замечаний | Зачтено |
|---|---|---:|---:|---:|
| [dispatch · 1](benchmark-runs/dispatch/r1/report.md) | dev | 5 | 5 | 4 |
| [dispatch · 2](benchmark-runs/dispatch/r2/report.md) | dev | 5 | 5 | 4 |
| [dispatch · 3](benchmark-runs/dispatch/r3/report.md) | dev | 5 | 7 | 5 |
| [dispatch-base · 1](benchmark-runs/dispatch-base/r1/report.md) | dev | 0 | 1 | 0 |
| [dispatch-base · 2](benchmark-runs/dispatch-base/r2/report.md) | dev | 0 | 3 | 0 |
| [dispatch-base · 3](benchmark-runs/dispatch-base/r3/report.md) | dev | 0 | 3 | 0 |
| [indicator · 1](benchmark-runs/indicator/r1/report.md) | test | 0 | 0 | 0 |
| [indicator · 2](benchmark-runs/indicator/r2/report.md) | test | 0 | 0 | 0 |
| [indicator · 3](benchmark-runs/indicator/r3/report.md) | test | 0 | 0 | 0 |
| [irrigation · 1](benchmark-runs/irrigation/r1/report.md) | test | 5 | 9 | 4 |
| [irrigation · 2](benchmark-runs/irrigation/r2/report.md) | test | 5 | 10 | 3 |
| [irrigation · 3](benchmark-runs/irrigation/r3/report.md) | test | 5 | 10 | 2 |
| [irrigation-base · 1](benchmark-runs/irrigation-base/r1/report.md) | test | 0 | 5 | 0 |
| [irrigation-base · 2](benchmark-runs/irrigation-base/r2/report.md) | test | 0 | 6 | 0 |
| [irrigation-base · 3](benchmark-runs/irrigation-base/r3/report.md) | test | 0 | 6 | 0 |
| [subtitles · 1](benchmark-runs/subtitles/r1/report.md) | test | 5 | 6 | 5 |
| [subtitles · 2](benchmark-runs/subtitles/r2/report.md) | test | 5 | 6 | 5 |
| [subtitles · 3](benchmark-runs/subtitles/r3/report.md) | test | 5 | 5 | 5 |
| [subtitles-base · 1](benchmark-runs/subtitles-base/r1/report.md) | test | 0 | 2 | 0 |
| [subtitles-base · 2](benchmark-runs/subtitles-base/r2/report.md) | test | 0 | 2 | 0 |
| [subtitles-base · 3](benchmark-runs/subtitles-base/r3/report.md) | test | 0 | 3 | 0 |

## Воспроизводимость замечаний

В одном документе сравниваются независимо полученные находки одной категории, у которых есть общая строка доказательства во всех вошедших прогонах и не более одного замечания в каждом. Конкурирующие или транзитивные совпадения показаны по отдельности и не дают балла устойчивости.

| ТЗ | Замечание | Категория | Частота | Прогон и ID |
|---|---|---|---:|---|
| dispatch | Отправка черновика | Противоречивость | 1/3 · спорное соответствие | [1/Z-001](benchmark-runs/dispatch/r1/report.md#z-001) |
| dispatch | Отправка ведомости из 25 строк | Противоречивость | 1/3 · спорное соответствие | [1/Z-004](benchmark-runs/dispatch/r1/report.md#z-004) |
| dispatch | Отправка черновика | Противоречивость | 1/3 · спорное соответствие | [2/Z-001](benchmark-runs/dispatch/r2/report.md#z-001) |
| dispatch | Отправка ведомости с 25 строками | Противоречивость | 1/3 · спорное соответствие | [2/Z-002](benchmark-runs/dispatch/r2/report.md#z-002) |
| dispatch | Отправка черновика | Противоречивость | 1/3 · спорное соответствие | [3/Z-001](benchmark-runs/dispatch/r3/report.md#z-001) |
| dispatch | Разрешение отправки ведомости из 25 строк | Противоречивость | 1/3 · спорное соответствие | [3/Z-002](benchmark-runs/dispatch/r3/report.md#z-002) |
| dispatch | Момент передачи черновика | Проверяемость | 3/3 | [1/Z-003](benchmark-runs/dispatch/r1/report.md#z-003), [2/Z-003](benchmark-runs/dispatch/r2/report.md#z-003), [3/Z-006](benchmark-runs/dispatch/r3/report.md#z-006) |
| dispatch | Задержка надписи «Передано» | Проверяемость | 3/3 | [1/Z-005](benchmark-runs/dispatch/r1/report.md#z-005), [2/Z-004](benchmark-runs/dispatch/r2/report.md#z-004), [3/Z-004](benchmark-runs/dispatch/r3/report.md#z-004) |
| dispatch | Ссылка на текст при отказе | Трассируемость | 3/3 | [1/Z-006](benchmark-runs/dispatch/r1/report.md#z-006), [2/Z-006](benchmark-runs/dispatch/r2/report.md#z-006), [3/Z-007](benchmark-runs/dispatch/r3/report.md#z-007) |
| dispatch | Если сохранится передача по попытке отправки из «Черновика», в каком состоянии должна быть ведомость при поступлении отказа перевозчика? | Полнота | 1/3 | [3/Z-003](benchmark-runs/dispatch/r3/report.md#z-003) |
| dispatch | Срок хранения подтверждения для значения 7 | Противоречивость | 1/3 | [3/Z-005](benchmark-runs/dispatch/r3/report.md#z-005) |
| dispatch-base | Три секунды для сообщения «Передано» | Однозначность | 3/3 | [1/Z-001](benchmark-runs/dispatch-base/r1/report.md#z-001), [2/Z-002](benchmark-runs/dispatch-base/r2/report.md#z-002), [3/Z-001](benchmark-runs/dispatch-base/r3/report.md#z-001) |
| dispatch-base | В каком состоянии должна быть ведомость после подтверждения перевозчика? | Полнота | 1/3 | [2/Z-001](benchmark-runs/dispatch-base/r2/report.md#z-001) |
| dispatch-base | Проверка причины отклонения файла | Проверяемость | 2/3 | [2/Z-003](benchmark-runs/dispatch-base/r2/report.md#z-003), [3/Z-003](benchmark-runs/dispatch-base/r3/report.md#z-003) |
| dispatch-base | От какого события отсчитываются семь суток локального хранения подтверждения при значении 7? | Полнота | 1/3 | [3/Z-002](benchmark-runs/dispatch-base/r3/report.md#z-002) |
| irrigation | Какие действия контроллера зависят от допустимых показаний влажности и при каких условиях выполняется каждое действие? | Полнота | 1/3 · спорное соответствие | [1/Z-001](benchmark-runs/irrigation/r1/report.md#z-001) |
| irrigation | В каком положении должен оказаться уже открытый клапан после нажатия кнопки ручной остановки, если новых команд открытия нет? | Полнота | 1/3 · спорное соответствие | [1/Z-003](benchmark-runs/irrigation/r1/report.md#z-003) |
| irrigation | Как корректные показания влажности определяют действие клапана, когда ручная остановка не активна и команды расписания нет? | Полнота | 1/3 · спорное соответствие | [2/Z-002](benchmark-runs/irrigation/r2/report.md#z-002) |
| irrigation | В каком положении должен оказаться уже открытый клапан после нажатия ручной остановки, если новых команд нет? | Полнота | 1/3 · спорное соответствие | [2/Z-004](benchmark-runs/irrigation/r2/report.md#z-004) |
| irrigation | Какое действие ожидается при заданном корректном показании и исходном состоянии секции вне ручной остановки, если команды расписания нет? | Полнота | 1/3 · спорное соответствие | [3/Z-001](benchmark-runs/irrigation/r3/report.md#z-001) |
| irrigation | В каком состоянии должен оказаться открытый клапан после нажатия кнопки ручной остановки, если новых команд открытия нет? | Полнота | 1/3 · спорное соответствие | [3/Z-004](benchmark-runs/irrigation/r3/report.md#z-004) |
| irrigation | Какое значение контроллер передаёт панели и из каких данных оно получается? | Полнота | 3/3 | [1/Z-002](benchmark-runs/irrigation/r1/report.md#z-002), [2/Z-003](benchmark-runs/irrigation/r2/report.md#z-003), [3/Z-003](benchmark-runs/irrigation/r3/report.md#z-003) |
| irrigation | Открытие по расписанию после ручной остановки | Противоречивость | 3/3 | [1/Z-004](benchmark-runs/irrigation/r1/report.md#z-004), [2/Z-005](benchmark-runs/irrigation/r2/report.md#z-005), [3/Z-005](benchmark-runs/irrigation/r3/report.md#z-005) |
| irrigation | Если открытие по расписанию при ручной остановке останется обязательным, между какими наблюдаемыми событиями измерять задержку и какой критерий считать выполнением требования «немедленно»? | Полнота | 3/3 | [1/Z-005](benchmark-runs/irrigation/r1/report.md#z-005), [2/Z-010](benchmark-runs/irrigation/r2/report.md#z-010), [3/Z-010](benchmark-runs/irrigation/r3/report.md#z-010) |
| irrigation | Критерий проверки кнопки «Возобновить» | Проверяемость | 3/3 | [1/Z-006](benchmark-runs/irrigation/r1/report.md#z-006), [2/Z-006](benchmark-runs/irrigation/r2/report.md#z-006), [3/Z-006](benchmark-runs/irrigation/r3/report.md#z-006) |
| irrigation | Категория омега | Ясность | 1/3 | [1/Z-007](benchmark-runs/irrigation/r1/report.md#z-007) |
| irrigation | Аварийный переход клапана | Полнота | 1/3 · спорное соответствие | [1/Z-008](benchmark-runs/irrigation/r1/report.md#z-008) |
| irrigation | По какому правилу контроллер определяет, что полученное показание некорректно? | Полнота | 1/3 · спорное соответствие | [2/Z-001](benchmark-runs/irrigation/r2/report.md#z-001) |
| irrigation | По какому критерию полученное показание считается некорректным и требует аварийного перехода? | Полнота | 1/3 · спорное соответствие | [3/Z-002](benchmark-runs/irrigation/r3/report.md#z-002) |
| irrigation | Аварийное положение клапана | Полнота | 1/3 · спорное соответствие | [3/Z-008](benchmark-runs/irrigation/r3/report.md#z-008) |
| irrigation | Число повторов после первого таймаута | Противоречивость | 3/3 | [1/Z-009](benchmark-runs/irrigation/r1/report.md#z-009), [2/Z-009](benchmark-runs/irrigation/r2/report.md#z-009), [3/Z-009](benchmark-runs/irrigation/r3/report.md#z-009) |
| irrigation | По какому признаку или перечню определить, что зона относится к категории омега? | Полнота | 2/3 | [2/Z-007](benchmark-runs/irrigation/r2/report.md#z-007), [3/Z-007](benchmark-runs/irrigation/r3/report.md#z-007) |
| irrigation | Ссылка на аварийное положение клапана | Трассируемость | 1/3 | [2/Z-008](benchmark-runs/irrigation/r2/report.md#z-008) |
| irrigation-base | Какое значение контроллер передаёт на панель и по каким исходным данным его определить? | Полнота | 3/3 | [1/Z-001](benchmark-runs/irrigation-base/r1/report.md#z-001), [2/Z-002](benchmark-runs/irrigation-base/r2/report.md#z-002), [3/Z-003](benchmark-runs/irrigation-base/r3/report.md#z-003) |
| irrigation-base | По какому критерию контроллер должен считать полученное показание некорректным? | Полнота | 1/3 · спорное соответствие | [1/Z-002](benchmark-runs/irrigation-base/r1/report.md#z-002) |
| irrigation-base | Входит ли в проверку возобновления поступление очередной команды открытия и некорректного показания в один шаг обработки? Если входит, в каком порядке должны исполниться команда и аварийное закрытие и каким должно быть итоговое положение клапана? | Полнота | 1/3 · спорное соответствие | [1/Z-005](benchmark-runs/irrigation-base/r1/report.md#z-005) |
| irrigation-base | По каким признакам полученное показание датчика следует считать некорректным для применения W-4? | Полнота | 1/3 · спорное соответствие | [2/Z-004](benchmark-runs/irrigation-base/r2/report.md#z-004) |
| irrigation-base | Могут ли очередная команда открытия после нажатия «Возобновить» и некорректное показание поступить одновременно? Если да, каким должно быть положение клапана после обработки обоих событий? | Полнота | 1/3 · спорное соответствие | [2/Z-005](benchmark-runs/irrigation-base/r2/report.md#z-005) |
| irrigation-base | Как корректное показание влажности влияет на управление клапаном при выбранной зоне и снятой ручной остановке? | Полнота | 1/3 · спорное соответствие | [1/Z-003](benchmark-runs/irrigation-base/r1/report.md#z-003) |
| irrigation-base | Какое положение должен принять уже открытый клапан после ручной остановки, если новых команд нет? | Полнота | 1/3 · спорное соответствие | [1/Z-004](benchmark-runs/irrigation-base/r1/report.md#z-004) |
| irrigation-base | При каких допустимых показаниях контроллер должен открыть закрытый клапан выбранной зоны, если ручная остановка снята? | Полнота | 1/3 · спорное соответствие | [2/Z-001](benchmark-runs/irrigation-base/r2/report.md#z-001) |
| irrigation-base | Каким должно быть положение уже открытого клапана после нажатия кнопки ручной остановки до поступления следующей команды? | Полнота | 1/3 · спорное соответствие | [2/Z-003](benchmark-runs/irrigation-base/r2/report.md#z-003) |
| irrigation-base | Как корректные показания влажности влияют на управление поливом в автоматическом режиме? | Полнота | 1/3 · спорное соответствие | [3/Z-002](benchmark-runs/irrigation-base/r3/report.md#z-002) |
| irrigation-base | В какое состояние должен перейти уже открытый клапан при нажатии кнопки ручной остановки во время полива? | Полнота | 1/3 · спорное соответствие | [3/Z-004](benchmark-runs/irrigation-base/r3/report.md#z-004) |
| irrigation-base | Дублирование числа повторов | Дублирование | 2/3 | [2/Z-006](benchmark-runs/irrigation-base/r2/report.md#z-006), [3/Z-006](benchmark-runs/irrigation-base/r3/report.md#z-006) |
| irrigation-base | Критерий некорректного показания | Проверяемость | 1/3 | [3/Z-001](benchmark-runs/irrigation-base/r3/report.md#z-001) |
| irrigation-base | Повтор правила о команде расписания | Дублирование | 1/3 | [3/Z-005](benchmark-runs/irrigation-base/r3/report.md#z-005) |
| subtitles | Что должно произойти с существующим файлом назначения и допустимой репликой, если другую реплику требуется отклонить по согласованному правилу длины? | Полнота | 2/3 | [1/Z-001](benchmark-runs/subtitles/r1/report.md#z-001), [2/Z-001](benchmark-runs/subtitles/r2/report.md#z-001) |
| subtitles | UTF-8 BOM в начале файла | Противоречивость | 3/3 | [1/Z-002](benchmark-runs/subtitles/r1/report.md#z-002), [2/Z-002](benchmark-runs/subtitles/r2/report.md#z-002), [3/Z-001](benchmark-runs/subtitles/r3/report.md#z-001) |
| subtitles | Шкала временных меток | Противоречивость | 3/3 | [1/Z-003](benchmark-runs/subtitles/r1/report.md#z-003), [2/Z-003](benchmark-runs/subtitles/r2/report.md#z-003), [3/Z-002](benchmark-runs/subtitles/r3/report.md#z-002) |
| subtitles | Критерий лёгкости экспорта | Проверяемость | 3/3 | [1/Z-004](benchmark-runs/subtitles/r1/report.md#z-004), [2/Z-004](benchmark-runs/subtitles/r2/report.md#z-004), [3/Z-003](benchmark-runs/subtitles/r3/report.md#z-003) |
| subtitles | Приёмка реплики на границе длины | Противоречивость | 3/3 | [1/Z-005](benchmark-runs/subtitles/r1/report.md#z-005), [2/Z-005](benchmark-runs/subtitles/r2/report.md#z-005), [3/Z-005](benchmark-runs/subtitles/r3/report.md#z-005) |
| subtitles | Ссылка на текст сообщения пустой дорожки | Трассируемость | 3/3 | [1/Z-006](benchmark-runs/subtitles/r1/report.md#z-006), [2/Z-006](benchmark-runs/subtitles/r2/report.md#z-006), [3/Z-004](benchmark-runs/subtitles/r3/report.md#z-004) |
| subtitles-base | Обозначение миллисекунд в поле | Проверяемость | 3/3 | [1/Z-001](benchmark-runs/subtitles-base/r1/report.md#z-001), [2/Z-002](benchmark-runs/subtitles-base/r2/report.md#z-002), [3/Z-002](benchmark-runs/subtitles-base/r3/report.md#z-002) |
| subtitles-base | Какой результат по указанному пути ожидается при экспорте дорожки с репликами длиной 80 и 81 кодовая точка Unicode, если путь свободен, а более длинная реплика отклоняется? | Полнота | 3/3 | [1/Z-002](benchmark-runs/subtitles-base/r1/report.md#z-002), [2/Z-001](benchmark-runs/subtitles-base/r2/report.md#z-001), [3/Z-001](benchmark-runs/subtitles-base/r3/report.md#z-001) |
| subtitles-base | Как при приёмке определить, какая рабочая станция обозначена ST-1? | Полнота | 1/3 | [3/Z-003](benchmark-runs/subtitles-base/r3/report.md#z-003) |
