# Качество на размеченном корпусе

Дата оценки 2026-11-27T02:05:06+05:00. Провайдер и модель — OpenAI через Codex CLI · gpt-6.2-sol. Коммит реализации — `5e390952fe85b4739ad9923165a4a7a076020cc9`.

Основной результат измерен по первому запуску каждого документа. Полнота — **15/15 (100.0%)**. Точность — **15/26 (57.7%)**.

Во всех 3 прогонах воспроизвелось **18/37 (48.6%)** групп замечаний.

## Метод

Разметка и базовые версии не включаются в запросы модели. Балл даётся за точную категорию и пересечение цитат со всеми раздельно заданными диапазонами дефекта. Только одна пара «замечание — дефект» может получить балл. Конкурирующие пары и совпадения лишь по строкам остаются незачтёнными. Требования к совпадению зафиксированы до измерения. В знаменатель точности входят все опубликованные карточки Z, включая вопросы и рекомендации. Существование других реальных дефектов, включая контрольные документы, возможно. [Незачтённые замечания для проверки человеком](evaluation-manual.md)

Результаты dev и test приведены отдельно. Dev служит для разработки. Разметка test предназначена для измерения после фиксации механизма и не должна применяться для подбора подсказок.

| Часть | Прогон | Полнота | Точность |
|---|---:|---:|---:|
| all | 1 | 15/15 (100.0%) | 15/26 (57.7%) |
| all | 2 | 14/15 (93.3%) | 14/24 (58.3%) |
| all | 3 | 15/15 (100.0%) | 15/27 (55.6%) |
| dev | 1 | 5/5 (100.0%) | 5/6 (83.3%) |
| dev | 2 | 5/5 (100.0%) | 5/7 (71.4%) |
| dev | 3 | 5/5 (100.0%) | 5/7 (71.4%) |
| test | 1 | 10/10 (100.0%) | 10/20 (50.0%) |
| test | 2 | 9/10 (90.0%) | 9/17 (52.9%) |
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
| отсутствие обработки ошибки | 2 | 0/1 (0.0%) |
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
| dispatch / dev | D-02 | разные числа для одного параметра | Противоречивость | 10, 11 | Файл из 25 строк принят при максимуме 24. | [Z-002](benchmark-runs/dispatch/r1/report.md#z-002) · [Z-002](benchmark-runs/dispatch/r2/report.md#z-002) · [Z-002](benchmark-runs/dispatch/r3/report.md#z-002) |
| dispatch / dev | D-03 | расплывчатый срок | Проверяемость | 12 | «Достаточно быстро» не задаёт предела для отображения результата. | [Z-005](benchmark-runs/dispatch/r1/report.md#z-005) · [Z-005](benchmark-runs/dispatch/r2/report.md#z-005) · [Z-005](benchmark-runs/dispatch/r3/report.md#z-005) |
| dispatch / dev | D-04 | ссылка на несуществующий ID | Трассируемость | 13 | Для сообщения об отказе указана отсутствующая норма S-97. | [Z-006](benchmark-runs/dispatch/r1/report.md#z-006) · [Z-006](benchmark-runs/dispatch/r2/report.md#z-006) · [Z-006](benchmark-runs/dispatch/r3/report.md#z-006) |
| dispatch / dev | D-05 | несовпадение единиц | Противоречивость | 15 | Один параметр измеряется в сутках, но его значение интерпретируется как часы. | [Z-003](benchmark-runs/dispatch/r1/report.md#z-003) · [Z-003](benchmark-runs/dispatch/r2/report.md#z-003) · [Z-003](benchmark-runs/dispatch/r3/report.md#z-003) |
| irrigation / test | I-01 | противоречие между правилами | Противоречивость | 6, 7 | Автоматика одновременно игнорирует команду и открывает клапан при ручной остановке. | [Z-004](benchmark-runs/irrigation/r1/report.md#z-004) · [Z-003](benchmark-runs/irrigation/r2/report.md#z-003) · [Z-004](benchmark-runs/irrigation/r3/report.md#z-004) |
| irrigation / test | I-02 | неопределённый термин | Ясность | 8 | Не определены признаки зоны категории омега. | [Z-006](benchmark-runs/irrigation/r1/report.md#z-006) · [Z-006](benchmark-runs/irrigation/r2/report.md#z-006) · [Z-006](benchmark-runs/irrigation/r3/report.md#z-006) |
| irrigation / test | I-03 | отсутствие обработки ошибки | Полнота | 9 | Документ требует аварийного положения клапана, но убрано указание, какое положение выбрать при некорректном датчике. | [Z-007](benchmark-runs/irrigation/r1/report.md#z-007) · пропуск · [Z-007](benchmark-runs/irrigation/r3/report.md#z-007) |
| irrigation / test | I-04 | отсутствие критерия приёмки | Полнота | 10 | Обязательному испытанию кнопки не заданы шаг и ожидаемый результат. | [Z-005](benchmark-runs/irrigation/r1/report.md#z-005) · [Z-004](benchmark-runs/irrigation/r2/report.md#z-004) · [Z-005](benchmark-runs/irrigation/r3/report.md#z-005) |
| irrigation / test | I-05 | дублирование с разными значениями | Противоречивость | 13, 14 | Для одной и той же повторной передачи предписаны три и пять повторов. | [Z-008](benchmark-runs/irrigation/r1/report.md#z-008) · [Z-007](benchmark-runs/irrigation/r2/report.md#z-007) · [Z-008](benchmark-runs/irrigation/r3/report.md#z-008) |
| subtitles / test | S-01 | противоречие между правилами | Противоречивость | 6, 7 | Маркер BOM одновременно обязателен и запрещён. | [Z-001](benchmark-runs/subtitles/r1/report.md#z-001) · [Z-001](benchmark-runs/subtitles/r2/report.md#z-001) · [Z-001](benchmark-runs/subtitles/r3/report.md#z-001) |
| subtitles / test | S-02 | несовпадение единиц | Противоречивость | 8 | 1000 мс названы одной минутой. | [Z-002](benchmark-runs/subtitles/r1/report.md#z-002) · [Z-002](benchmark-runs/subtitles/r2/report.md#z-002) · [Z-002](benchmark-runs/subtitles/r3/report.md#z-002) |
| subtitles / test | S-03 | непроверяемое нефункциональное требование | Проверяемость | 9 | Нет объективного способа принять «effortless to every user». | [Z-004](benchmark-runs/subtitles/r1/report.md#z-004) · [Z-003](benchmark-runs/subtitles/r2/report.md#z-003) · [Z-003](benchmark-runs/subtitles/r3/report.md#z-003) |
| subtitles / test | S-04 | ссылка на несуществующий ID | Трассируемость | 10 | Указан отсутствующий T-40 вместо существующего описания сообщения. | [Z-005](benchmark-runs/subtitles/r1/report.md#z-005) · [Z-005](benchmark-runs/subtitles/r2/report.md#z-005) · [Z-005](benchmark-runs/subtitles/r3/report.md#z-005) |
| subtitles / test | S-05 | разные числа для одного параметра | Противоречивость | 14, 15 | Тест принимает длину 81 при предельной длине 80. | [Z-003](benchmark-runs/subtitles/r1/report.md#z-003) · [Z-004](benchmark-runs/subtitles/r2/report.md#z-004) · [Z-004](benchmark-runs/subtitles/r3/report.md#z-004) |

## Сохранённые отчёты и контрольные документы

| Отчёт и прогон | Часть | Заложено | Замечаний | Зачтено |
|---|---|---:|---:|---:|
| [dispatch · 1](benchmark-runs/dispatch/r1/report.md) | dev | 5 | 5 | 5 |
| [dispatch · 2](benchmark-runs/dispatch/r2/report.md) | dev | 5 | 5 | 5 |
| [dispatch · 3](benchmark-runs/dispatch/r3/report.md) | dev | 5 | 5 | 5 |
| [dispatch-base · 1](benchmark-runs/dispatch-base/r1/report.md) | dev | 0 | 1 | 0 |
| [dispatch-base · 2](benchmark-runs/dispatch-base/r2/report.md) | dev | 0 | 2 | 0 |
| [dispatch-base · 3](benchmark-runs/dispatch-base/r3/report.md) | dev | 0 | 2 | 0 |
| [indicator · 1](benchmark-runs/indicator/r1/report.md) | test | 0 | 0 | 0 |
| [indicator · 2](benchmark-runs/indicator/r2/report.md) | test | 0 | 0 | 0 |
| [indicator · 3](benchmark-runs/indicator/r3/report.md) | test | 0 | 0 | 0 |
| [irrigation · 1](benchmark-runs/irrigation/r1/report.md) | test | 5 | 8 | 5 |
| [irrigation · 2](benchmark-runs/irrigation/r2/report.md) | test | 5 | 6 | 4 |
| [irrigation · 3](benchmark-runs/irrigation/r3/report.md) | test | 5 | 8 | 5 |
| [irrigation-base · 1](benchmark-runs/irrigation-base/r1/report.md) | test | 0 | 5 | 0 |
| [irrigation-base · 2](benchmark-runs/irrigation-base/r2/report.md) | test | 0 | 4 | 0 |
| [irrigation-base · 3](benchmark-runs/irrigation-base/r3/report.md) | test | 0 | 5 | 0 |
| [subtitles · 1](benchmark-runs/subtitles/r1/report.md) | test | 5 | 5 | 5 |
| [subtitles · 2](benchmark-runs/subtitles/r2/report.md) | test | 5 | 5 | 5 |
| [subtitles · 3](benchmark-runs/subtitles/r3/report.md) | test | 5 | 5 | 5 |
| [subtitles-base · 1](benchmark-runs/subtitles-base/r1/report.md) | test | 0 | 2 | 0 |
| [subtitles-base · 2](benchmark-runs/subtitles-base/r2/report.md) | test | 0 | 2 | 0 |
| [subtitles-base · 3](benchmark-runs/subtitles-base/r3/report.md) | test | 0 | 2 | 0 |

## Воспроизводимость замечаний

В одном документе сравниваются независимо полученные находки одной категории, у которых есть общая строка доказательства во всех вошедших прогонах и не более одного замечания в каждом. Конкурирующие или транзитивные совпадения показаны по отдельности и не дают балла устойчивости.

| ТЗ | Замечание | Категория | Частота | Прогон и ID |
|---|---|---|---:|---|
| dispatch | Отправка черновика | Противоречивость | 1/3 · спорное соответствие | [1/Z-001](benchmark-runs/dispatch/r1/report.md#z-001) |
| dispatch | Ведомость из 25 строк | Противоречивость | 1/3 · спорное соответствие | [1/Z-002](benchmark-runs/dispatch/r1/report.md#z-002) |
| dispatch | Отправка из черновика | Противоречивость | 1/3 · спорное соответствие | [2/Z-001](benchmark-runs/dispatch/r2/report.md#z-001) |
| dispatch | Отправка ведомости из 25 строк | Противоречивость | 1/3 · спорное соответствие | [2/Z-002](benchmark-runs/dispatch/r2/report.md#z-002) |
| dispatch | Отправка черновика | Противоречивость | 1/3 · спорное соответствие | [3/Z-001](benchmark-runs/dispatch/r3/report.md#z-001) |
| dispatch | Вместимость ведомости | Противоречивость | 1/3 · спорное соответствие | [3/Z-002](benchmark-runs/dispatch/r3/report.md#z-002) |
| dispatch | Срок хранения при значении 7 | Противоречивость | 3/3 | [1/Z-003](benchmark-runs/dispatch/r1/report.md#z-003), [2/Z-003](benchmark-runs/dispatch/r2/report.md#z-003), [3/Z-003](benchmark-runs/dispatch/r3/report.md#z-003) |
| dispatch | Задержка показа «Передано» | Проверяемость | 3/3 | [1/Z-005](benchmark-runs/dispatch/r1/report.md#z-005), [2/Z-005](benchmark-runs/dispatch/r2/report.md#z-005), [3/Z-005](benchmark-runs/dispatch/r3/report.md#z-005) |
| dispatch | Отсутствует цель внутренней ссылки S-97 | Трассируемость | 3/3 | [1/Z-006](benchmark-runs/dispatch/r1/report.md#z-006), [2/Z-006](benchmark-runs/dispatch/r2/report.md#z-006), [3/Z-006](benchmark-runs/dispatch/r3/report.md#z-006) |
| dispatch-base | Три секунды для сообщения «Передано» | Однозначность | 3/3 | [1/Z-001](benchmark-runs/dispatch-base/r1/report.md#z-001), [2/Z-002](benchmark-runs/dispatch-base/r2/report.md#z-002), [3/Z-002](benchmark-runs/dispatch-base/r3/report.md#z-002) |
| dispatch-base | Какое состояние должна иметь та же ведомость после обработки подтверждения перевозчика? | Полнота | 2/3 | [2/Z-001](benchmark-runs/dispatch-base/r2/report.md#z-001), [3/Z-001](benchmark-runs/dispatch-base/r3/report.md#z-001) |
| irrigation | Какое состояние полива должно получиться для каждого допустимого показания и исходного состояния полива, когда ручная остановка не активна и команды от расписания нет? | Полнота | 2/3 | [1/Z-001](benchmark-runs/irrigation/r1/report.md#z-001), [3/Z-001](benchmark-runs/irrigation/r3/report.md#z-001) |
| irrigation | По какому правилу контроллер относит полученное показание влажности к некорректным для применения W-4? | Ясность | 3/3 | [1/Z-002](benchmark-runs/irrigation/r1/report.md#z-002), [2/Z-001](benchmark-runs/irrigation/r2/report.md#z-001), [3/Z-002](benchmark-runs/irrigation/r3/report.md#z-002) |
| irrigation | Из каких данных и по какому правилу определяется значение, передаваемое контроллером на панель? | Трассируемость | 3/3 | [1/Z-003](benchmark-runs/irrigation/r1/report.md#z-003), [2/Z-002](benchmark-runs/irrigation/r2/report.md#z-002), [3/Z-003](benchmark-runs/irrigation/r3/report.md#z-003) |
| irrigation | Открытие по расписанию при ручной остановке | Противоречивость | 3/3 | [1/Z-004](benchmark-runs/irrigation/r1/report.md#z-004), [2/Z-003](benchmark-runs/irrigation/r2/report.md#z-003), [3/Z-004](benchmark-runs/irrigation/r3/report.md#z-004) |
| irrigation | Приёмочное испытание кнопки «Возобновить» | Полнота | 3/3 | [1/Z-005](benchmark-runs/irrigation/r1/report.md#z-005), [2/Z-004](benchmark-runs/irrigation/r2/report.md#z-004), [3/Z-005](benchmark-runs/irrigation/r3/report.md#z-005) |
| irrigation | По какому признаку определить, что включённая зона относится к категории омега? | Ясность | 3/3 | [1/Z-006](benchmark-runs/irrigation/r1/report.md#z-006), [2/Z-006](benchmark-runs/irrigation/r2/report.md#z-006), [3/Z-006](benchmark-runs/irrigation/r3/report.md#z-006) |
| irrigation | Аварийное положение клапана | Полнота | 2/3 | [1/Z-007](benchmark-runs/irrigation/r1/report.md#z-007), [3/Z-007](benchmark-runs/irrigation/r3/report.md#z-007) |
| irrigation | Число повторов передачи после таймаута | Противоречивость | 3/3 | [1/Z-008](benchmark-runs/irrigation/r1/report.md#z-008), [2/Z-007](benchmark-runs/irrigation/r2/report.md#z-007), [3/Z-008](benchmark-runs/irrigation/r3/report.md#z-008) |
| irrigation-base | Какое положение должен принять клапан при получении корректного показания влажности в зависимости от показания и исходного положения клапана, если зона выбрана и ручная остановка снята? | Полнота | 1/3 · спорное соответствие | [1/Z-001](benchmark-runs/irrigation-base/r1/report.md#z-001) |
| irrigation-base | Должен ли уже открытый клапан закрыться от самого нажатия кнопки ручной остановки при отсутствии других событий? | Полнота | 1/3 · спорное соответствие | [1/Z-004](benchmark-runs/irrigation-base/r1/report.md#z-004) |
| irrigation-base | Какое положение клапана должен обеспечить контроллер при каждом корректном показании влажности с учётом исходного положения клапана, если зона выбрана, автоматика активна и команды расписания нет? | Полнота | 1/3 · спорное соответствие | [2/Z-001](benchmark-runs/irrigation-base/r2/report.md#z-001) |
| irrigation-base | Какое положение должен занять уже открытый клапан после нажатия кнопки ручной остановки, если других команд нет и блокировка последующих автоматических команд открытия действует до возобновления? | Полнота | 1/3 · спорное соответствие | [2/Z-003](benchmark-runs/irrigation-base/r2/report.md#z-003) |
| irrigation-base | Какое состояние клапана должна установить автоматика в выбранной зоне в зависимости от корректного показания влажности? | Полнота | 1/3 · спорное соответствие | [3/Z-001](benchmark-runs/irrigation-base/r3/report.md#z-001) |
| irrigation-base | В каком положении должен оказаться уже открытый клапан непосредственно после нажатия кнопки ручной остановки? | Полнота | 1/3 · спорное соответствие | [3/Z-003](benchmark-runs/irrigation-base/r3/report.md#z-003) |
| irrigation-base | Из каких исходных данных определяется значение, которое контроллер повторно передаёт панели после первого таймаута? | Трассируемость | 3/3 | [1/Z-002](benchmark-runs/irrigation-base/r1/report.md#z-002), [2/Z-002](benchmark-runs/irrigation-base/r2/report.md#z-002), [3/Z-002](benchmark-runs/irrigation-base/r3/report.md#z-002) |
| irrigation-base | По какому критерию контроллер должен относить показание датчика влажности к некорректным для применения W-4? | Ясность | 3/3 | [1/Z-003](benchmark-runs/irrigation-base/r1/report.md#z-003), [2/Z-004](benchmark-runs/irrigation-base/r2/report.md#z-004), [3/Z-004](benchmark-runs/irrigation-base/r3/report.md#z-004) |
| irrigation-base | Дублирование числа повторов | Дублирование | 2/3 | [1/Z-005](benchmark-runs/irrigation-base/r1/report.md#z-005), [3/Z-005](benchmark-runs/irrigation-base/r3/report.md#z-005) |
| subtitles | BOM в начале файла | Противоречивость | 3/3 | [1/Z-001](benchmark-runs/subtitles/r1/report.md#z-001), [2/Z-001](benchmark-runs/subtitles/r2/report.md#z-001), [3/Z-001](benchmark-runs/subtitles/r3/report.md#z-001) |
| subtitles | Масштаб временных меток | Противоречивость | 3/3 | [1/Z-002](benchmark-runs/subtitles/r1/report.md#z-002), [2/Z-002](benchmark-runs/subtitles/r2/report.md#z-002), [3/Z-002](benchmark-runs/subtitles/r3/report.md#z-002) |
| subtitles | Реплика из 81 кодовой точки | Противоречивость | 3/3 | [1/Z-003](benchmark-runs/subtitles/r1/report.md#z-003), [2/Z-004](benchmark-runs/subtitles/r2/report.md#z-004), [3/Z-004](benchmark-runs/subtitles/r3/report.md#z-004) |
| subtitles | Критерий лёгкости экспорта | Проверяемость | 3/3 | [1/Z-004](benchmark-runs/subtitles/r1/report.md#z-004), [2/Z-003](benchmark-runs/subtitles/r2/report.md#z-003), [3/Z-003](benchmark-runs/subtitles/r3/report.md#z-003) |
| subtitles | Отсутствует цель внутренней ссылки T-40 | Трассируемость | 3/3 | [1/Z-005](benchmark-runs/subtitles/r1/report.md#z-005), [2/Z-005](benchmark-runs/subtitles/r2/report.md#z-005), [3/Z-005](benchmark-runs/subtitles/r3/report.md#z-005) |
| subtitles-base | Каким должен быть существующий файл назначения после экспорта дорожки с одной допустимой репликой и одной отклонённой репликой из 81 кодовой точки Unicode? | Полнота | 3/3 | [1/Z-001](benchmark-runs/subtitles-base/r1/report.md#z-001), [2/Z-001](benchmark-runs/subtitles-base/r2/report.md#z-001), [3/Z-001](benchmark-runs/subtitles-base/r3/report.md#z-001) |
| subtitles-base | Где и по какой записи проверяющий должен подтверждать объявление миллисекунд для каждого поля временной метки? | Трассируемость | 1/3 | [1/Z-002](benchmark-runs/subtitles-base/r1/report.md#z-002) |
| subtitles-base | Как в экспортированном файле представлено объявление миллисекунд для каждого поля временной метки? | Полнота | 1/3 | [2/Z-002](benchmark-runs/subtitles-base/r2/report.md#z-002) |
| subtitles-base | По какому элементу экспортированного файла проверяющий должен распознать объявление миллисекунд для каждого поля временной метки? | Проверяемость | 1/3 | [3/Z-002](benchmark-runs/subtitles-base/r3/report.md#z-002) |
