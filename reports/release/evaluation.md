# Качество на размеченном корпусе

Дата оценки 2026-11-27T00:16:39+05:00. Провайдер и модель — OpenAI через Codex CLI · gpt-6.2-sol. Коммит реализации — `fa37472f35441307f7381e879654200a81cbb0aa`.

Основной результат измерен по первому запуску каждого документа. Полнота — **15/15 (100.0%)**. Точность — **15/24 (62.5%)**.

Во всех 3 прогонах воспроизвелось **18/37 (48.6%)** групп замечаний.

## Метод

Разметка и базовые версии не включаются в запросы модели. Балл даётся за точную категорию и пересечение цитат со всеми раздельно заданными диапазонами дефекта. Только одна пара «замечание — дефект» может получить балл. Конкурирующие пары и совпадения лишь по строкам остаются незачтёнными. Требования к совпадению зафиксированы до измерения. В знаменатель точности входят все опубликованные карточки Z, включая вопросы и рекомендации. Существование других реальных дефектов, включая контрольные документы, возможно. [Незачтённые замечания для проверки человеком](evaluation-manual.md)

Результаты dev и test приведены отдельно. Dev служит для разработки. Разметка test предназначена для измерения после фиксации механизма и не должна применяться для подбора подсказок.

| Часть | Прогон | Полнота | Точность |
|---|---:|---:|---:|
| all | 1 | 15/15 (100.0%) | 15/24 (62.5%) |
| all | 2 | 14/15 (93.3%) | 14/27 (51.9%) |
| all | 3 | 14/15 (93.3%) | 14/26 (53.8%) |
| dev | 1 | 5/5 (100.0%) | 5/6 (83.3%) |
| dev | 2 | 5/5 (100.0%) | 5/7 (71.4%) |
| dev | 3 | 5/5 (100.0%) | 5/7 (71.4%) |
| test | 1 | 10/10 (100.0%) | 10/18 (55.6%) |
| test | 2 | 9/10 (90.0%) | 9/20 (45.0%) |
| test | 3 | 9/10 (90.0%) | 9/19 (47.4%) |

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
| dispatch / dev | D-02 | разные числа для одного параметра | Противоречивость | 10, 11 | Файл из 25 строк принят при максимуме 24. | [Z-003](benchmark-runs/dispatch/r1/report.md#z-003) · [Z-002](benchmark-runs/dispatch/r2/report.md#z-002) · [Z-002](benchmark-runs/dispatch/r3/report.md#z-002) |
| dispatch / dev | D-03 | расплывчатый срок | Проверяемость | 12 | «Достаточно быстро» не задаёт предела для отображения результата. | [Z-004](benchmark-runs/dispatch/r1/report.md#z-004) · [Z-004](benchmark-runs/dispatch/r2/report.md#z-004) · [Z-004](benchmark-runs/dispatch/r3/report.md#z-004) |
| dispatch / dev | D-04 | ссылка на несуществующий ID | Трассируемость | 13 | Для сообщения об отказе указана отсутствующая норма S-97. | [Z-006](benchmark-runs/dispatch/r1/report.md#z-006) · [Z-006](benchmark-runs/dispatch/r2/report.md#z-006) · [Z-006](benchmark-runs/dispatch/r3/report.md#z-006) |
| dispatch / dev | D-05 | несовпадение единиц | Противоречивость | 15 | Один параметр измеряется в сутках, но его значение интерпретируется как часы. | [Z-005](benchmark-runs/dispatch/r1/report.md#z-005) · [Z-005](benchmark-runs/dispatch/r2/report.md#z-005) · [Z-005](benchmark-runs/dispatch/r3/report.md#z-005) |
| irrigation / test | I-01 | противоречие между правилами | Противоречивость | 6, 7 | Автоматика одновременно игнорирует команду и открывает клапан при ручной остановке. | [Z-003](benchmark-runs/irrigation/r1/report.md#z-003) · [Z-003](benchmark-runs/irrigation/r2/report.md#z-003) · [Z-003](benchmark-runs/irrigation/r3/report.md#z-003) |
| irrigation / test | I-02 | неопределённый термин | Ясность | 8 | Не определены признаки зоны категории омега. | [Z-006](benchmark-runs/irrigation/r1/report.md#z-006) · [Z-006](benchmark-runs/irrigation/r2/report.md#z-006) · [Z-006](benchmark-runs/irrigation/r3/report.md#z-006) |
| irrigation / test | I-03 | отсутствие обработки ошибки | Полнота | 9 | Документ требует аварийного положения клапана, но убрано указание, какое положение выбрать при некорректном датчике. | [Z-001](benchmark-runs/irrigation/r1/report.md#z-001) · пропуск · пропуск |
| irrigation / test | I-04 | отсутствие критерия приёмки | Полнота | 10 | Обязательному испытанию кнопки не заданы шаг и ожидаемый результат. | [Z-004](benchmark-runs/irrigation/r1/report.md#z-004) · [Z-004](benchmark-runs/irrigation/r2/report.md#z-004) · [Z-004](benchmark-runs/irrigation/r3/report.md#z-004) |
| irrigation / test | I-05 | дублирование с разными значениями | Противоречивость | 13, 14 | Для одной и той же повторной передачи предписаны три и пять повторов. | [Z-007](benchmark-runs/irrigation/r1/report.md#z-007) · [Z-009](benchmark-runs/irrigation/r2/report.md#z-009) · [Z-008](benchmark-runs/irrigation/r3/report.md#z-008) |
| subtitles / test | S-01 | противоречие между правилами | Противоречивость | 6, 7 | Маркер BOM одновременно обязателен и запрещён. | [Z-002](benchmark-runs/subtitles/r1/report.md#z-002) · [Z-001](benchmark-runs/subtitles/r2/report.md#z-001) · [Z-001](benchmark-runs/subtitles/r3/report.md#z-001) |
| subtitles / test | S-02 | несовпадение единиц | Противоречивость | 8 | 1000 мс названы одной минутой. | [Z-003](benchmark-runs/subtitles/r1/report.md#z-003) · [Z-002](benchmark-runs/subtitles/r2/report.md#z-002) · [Z-002](benchmark-runs/subtitles/r3/report.md#z-002) |
| subtitles / test | S-03 | непроверяемое нефункциональное требование | Проверяемость | 9 | Нет объективного способа принять «effortless to every user». | [Z-004](benchmark-runs/subtitles/r1/report.md#z-004) · [Z-003](benchmark-runs/subtitles/r2/report.md#z-003) · [Z-003](benchmark-runs/subtitles/r3/report.md#z-003) |
| subtitles / test | S-04 | ссылка на несуществующий ID | Трассируемость | 10 | Указан отсутствующий T-40 вместо существующего описания сообщения. | [Z-006](benchmark-runs/subtitles/r1/report.md#z-006) · [Z-005](benchmark-runs/subtitles/r2/report.md#z-005) · [Z-005](benchmark-runs/subtitles/r3/report.md#z-005) |
| subtitles / test | S-05 | разные числа для одного параметра | Противоречивость | 14, 15 | Тест принимает длину 81 при предельной длине 80. | [Z-005](benchmark-runs/subtitles/r1/report.md#z-005) · [Z-004](benchmark-runs/subtitles/r2/report.md#z-004) · [Z-004](benchmark-runs/subtitles/r3/report.md#z-004) |

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
| [irrigation · 1](benchmark-runs/irrigation/r1/report.md) | test | 5 | 6 | 5 |
| [irrigation · 2](benchmark-runs/irrigation/r2/report.md) | test | 5 | 8 | 4 |
| [irrigation · 3](benchmark-runs/irrigation/r3/report.md) | test | 5 | 8 | 4 |
| [irrigation-base · 1](benchmark-runs/irrigation-base/r1/report.md) | test | 0 | 5 | 0 |
| [irrigation-base · 2](benchmark-runs/irrigation-base/r2/report.md) | test | 0 | 5 | 0 |
| [irrigation-base · 3](benchmark-runs/irrigation-base/r3/report.md) | test | 0 | 4 | 0 |
| [subtitles · 1](benchmark-runs/subtitles/r1/report.md) | test | 5 | 6 | 5 |
| [subtitles · 2](benchmark-runs/subtitles/r2/report.md) | test | 5 | 5 | 5 |
| [subtitles · 3](benchmark-runs/subtitles/r3/report.md) | test | 5 | 5 | 5 |
| [subtitles-base · 1](benchmark-runs/subtitles-base/r1/report.md) | test | 0 | 1 | 0 |
| [subtitles-base · 2](benchmark-runs/subtitles-base/r2/report.md) | test | 0 | 2 | 0 |
| [subtitles-base · 3](benchmark-runs/subtitles-base/r3/report.md) | test | 0 | 2 | 0 |

## Воспроизводимость замечаний

В одном документе сравниваются независимо полученные находки одной категории, у которых есть общая строка доказательства во всех вошедших прогонах и не более одного замечания в каждом. Конкурирующие или транзитивные совпадения показаны по отдельности и не дают балла устойчивости.

| ТЗ | Замечание | Категория | Частота | Прогон и ID |
|---|---|---|---:|---|
| dispatch | Отправка черновика | Противоречивость | 1/3 · спорное соответствие | [1/Z-001](benchmark-runs/dispatch/r1/report.md#z-001) |
| dispatch | Отправка ведомости из 25 строк | Противоречивость | 1/3 · спорное соответствие | [1/Z-003](benchmark-runs/dispatch/r1/report.md#z-003) |
| dispatch | Передача черновика | Противоречивость | 1/3 · спорное соответствие | [2/Z-001](benchmark-runs/dispatch/r2/report.md#z-001) |
| dispatch | Допуск ведомости из 25 строк | Противоречивость | 1/3 · спорное соответствие | [2/Z-002](benchmark-runs/dispatch/r2/report.md#z-002) |
| dispatch | Отправка черновика | Противоречивость | 1/3 · спорное соответствие | [3/Z-001](benchmark-runs/dispatch/r3/report.md#z-001) |
| dispatch | Отправка ведомости из 25 строк | Противоречивость | 1/3 · спорное соответствие | [3/Z-002](benchmark-runs/dispatch/r3/report.md#z-002) |
| dispatch | Задержка показа подтверждения | Проверяемость | 3/3 | [1/Z-004](benchmark-runs/dispatch/r1/report.md#z-004), [2/Z-004](benchmark-runs/dispatch/r2/report.md#z-004), [3/Z-004](benchmark-runs/dispatch/r3/report.md#z-004) |
| dispatch | Единица срока хранения | Противоречивость | 3/3 | [1/Z-005](benchmark-runs/dispatch/r1/report.md#z-005), [2/Z-005](benchmark-runs/dispatch/r2/report.md#z-005), [3/Z-005](benchmark-runs/dispatch/r3/report.md#z-005) |
| dispatch | Отсутствует цель внутренней ссылки S-97 | Трассируемость | 3/3 | [1/Z-006](benchmark-runs/dispatch/r1/report.md#z-006), [2/Z-006](benchmark-runs/dispatch/r2/report.md#z-006), [3/Z-006](benchmark-runs/dispatch/r3/report.md#z-006) |
| dispatch-base | Значение трёх секунд показа | Однозначность | 3/3 | [1/Z-001](benchmark-runs/dispatch-base/r1/report.md#z-001), [2/Z-002](benchmark-runs/dispatch-base/r2/report.md#z-002), [3/Z-001](benchmark-runs/dispatch-base/r3/report.md#z-001) |
| dispatch-base | В каком состоянии должна быть ведомость после подтверждения отправки перевозчиком? | Полнота | 1/3 | [2/Z-001](benchmark-runs/dispatch-base/r2/report.md#z-001) |
| dispatch-base | Достаточно ли для подтверждения причины сравнить загрузку корректного файла с 24 строками и того же файла с добавленной 25-й строкой, или при отказе нужен отдельный наблюдаемый признак превышения лимита? | Полнота | 1/3 | [3/Z-002](benchmark-runs/dispatch-base/r3/report.md#z-002) |
| irrigation | Условия и результат аварийного перехода | Полнота | 2/3 | [1/Z-001](benchmark-runs/irrigation/r1/report.md#z-001), [2/Z-001](benchmark-runs/irrigation/r2/report.md#z-001) |
| irrigation | Какое значение контроллер передаёт панели и по какому входу или состоянию определить ожидаемое содержимое первого повтора? | Полнота | 3/3 | [1/Z-002](benchmark-runs/irrigation/r1/report.md#z-002), [2/Z-002](benchmark-runs/irrigation/r2/report.md#z-002), [3/Z-002](benchmark-runs/irrigation/r3/report.md#z-002) |
| irrigation | Открытие по расписанию при ручной остановке | Противоречивость | 3/3 | [1/Z-003](benchmark-runs/irrigation/r1/report.md#z-003), [2/Z-003](benchmark-runs/irrigation/r2/report.md#z-003), [3/Z-003](benchmark-runs/irrigation/r3/report.md#z-003) |
| irrigation | Приёмочное испытание кнопки «Возобновить» | Полнота | 3/3 | [1/Z-004](benchmark-runs/irrigation/r1/report.md#z-004), [2/Z-004](benchmark-runs/irrigation/r2/report.md#z-004), [3/Z-004](benchmark-runs/irrigation/r3/report.md#z-004) |
| irrigation | По какому признаку или перечню определить принадлежность включённой зоны к категории омега? | Ясность | 3/3 | [1/Z-006](benchmark-runs/irrigation/r1/report.md#z-006), [2/Z-006](benchmark-runs/irrigation/r2/report.md#z-006), [3/Z-006](benchmark-runs/irrigation/r3/report.md#z-006) |
| irrigation | Число повторных передач после таймаута | Противоречивость | 3/3 | [1/Z-007](benchmark-runs/irrigation/r1/report.md#z-007), [2/Z-009](benchmark-runs/irrigation/r2/report.md#z-009), [3/Z-008](benchmark-runs/irrigation/r3/report.md#z-008) |
| irrigation | Аварийное положение клапана | Трассируемость | 2/3 | [2/Z-007](benchmark-runs/irrigation/r2/report.md#z-007), [3/Z-007](benchmark-runs/irrigation/r3/report.md#z-007) |
| irrigation | По какому критерию показание датчика считается некорректным для применения W-4? | Ясность | 2/3 | [2/Z-008](benchmark-runs/irrigation/r2/report.md#z-008), [3/Z-001](benchmark-runs/irrigation/r3/report.md#z-001) |
| irrigation | Задержка открытия по расписанию | Проверяемость | 1/3 | [3/Z-005](benchmark-runs/irrigation/r3/report.md#z-005) |
| irrigation-base | Какое значение контроллер должен передать на панель при повторе и как определить его ожидаемое содержимое? | Полнота | 3/3 | [1/Z-001](benchmark-runs/irrigation-base/r1/report.md#z-001), [2/Z-002](benchmark-runs/irrigation-base/r2/report.md#z-002), [3/Z-002](benchmark-runs/irrigation-base/r3/report.md#z-002) |
| irrigation-base | По какому критерию контроллер должен относить полученное показание датчика влажности к некорректным? | Ясность | 3/3 | [1/Z-002](benchmark-runs/irrigation-base/r1/report.md#z-002), [2/Z-004](benchmark-runs/irrigation-base/r2/report.md#z-004), [3/Z-003](benchmark-runs/irrigation-base/r3/report.md#z-003) |
| irrigation-base | При каких корректных показаниях влажности контроллер должен открыть закрытый клапан вне ручной остановки и без команды расписания? | Полнота | 1/3 · спорное соответствие | [1/Z-003](benchmark-runs/irrigation-base/r1/report.md#z-003) |
| irrigation-base | Какое положение должен занять уже открытый клапан в результате нажатия кнопки ручной остановки? | Полнота | 1/3 · спорное соответствие | [1/Z-004](benchmark-runs/irrigation-base/r1/report.md#z-004) |
| irrigation-base | При каких корректных показаниях влажности контроллер должен начать полив выбранной зоны в штатном режиме? | Полнота | 1/3 · спорное соответствие | [2/Z-001](benchmark-runs/irrigation-base/r2/report.md#z-001) |
| irrigation-base | В каком положении должен быть уже открытый клапан после нажатия ручной остановки и до следующей команды? | Полнота | 1/3 · спорное соответствие | [2/Z-003](benchmark-runs/irrigation-base/r2/report.md#z-003) |
| irrigation-base | Какое состояние должен принять клапан выбранной зоны при каждом корректном показании влажности после возобновления автоматики с учётом исходного состояния клапана? | Полнота | 1/3 · спорное соответствие | [3/Z-001](benchmark-runs/irrigation-base/r3/report.md#z-001) |
| irrigation-base | Дублирование числа повторов | Дублирование | 3/3 | [1/Z-005](benchmark-runs/irrigation-base/r1/report.md#z-005), [2/Z-005](benchmark-runs/irrigation-base/r2/report.md#z-005), [3/Z-004](benchmark-runs/irrigation-base/r3/report.md#z-004) |
| subtitles | Каков ожидаемый результат записи в целевой файл при экспорте дорожки, в которой одна реплика допустима, а другая отклоняется по ограничению длины? | Полнота | 1/3 | [1/Z-001](benchmark-runs/subtitles/r1/report.md#z-001) |
| subtitles | BOM в начале файла | Противоречивость | 3/3 | [1/Z-002](benchmark-runs/subtitles/r1/report.md#z-002), [2/Z-001](benchmark-runs/subtitles/r2/report.md#z-001), [3/Z-001](benchmark-runs/subtitles/r3/report.md#z-001) |
| subtitles | Шкала временных меток | Противоречивость | 3/3 | [1/Z-003](benchmark-runs/subtitles/r1/report.md#z-003), [2/Z-002](benchmark-runs/subtitles/r2/report.md#z-002), [3/Z-002](benchmark-runs/subtitles/r3/report.md#z-002) |
| subtitles | Критерий удобства экспорта | Проверяемость | 3/3 | [1/Z-004](benchmark-runs/subtitles/r1/report.md#z-004), [2/Z-003](benchmark-runs/subtitles/r2/report.md#z-003), [3/Z-003](benchmark-runs/subtitles/r3/report.md#z-003) |
| subtitles | Реплика из 81 кодовой точки | Противоречивость | 3/3 | [1/Z-005](benchmark-runs/subtitles/r1/report.md#z-005), [2/Z-004](benchmark-runs/subtitles/r2/report.md#z-004), [3/Z-004](benchmark-runs/subtitles/r3/report.md#z-004) |
| subtitles | Ссылка на сообщение пустой дорожки | Трассируемость | 3/3 | [1/Z-006](benchmark-runs/subtitles/r1/report.md#z-006), [2/Z-005](benchmark-runs/subtitles/r2/report.md#z-005), [3/Z-005](benchmark-runs/subtitles/r3/report.md#z-005) |
| subtitles-base | При экспорте по новому пути дорожки с репликами длиной 80 и 81 кодовая точка Unicode должен ли появиться файл с 80-точечной репликой или файл не создаётся? | Полнота | 3/3 | [1/Z-001](benchmark-runs/subtitles-base/r1/report.md#z-001), [2/Z-002](benchmark-runs/subtitles-base/r2/report.md#z-002), [3/Z-001](benchmark-runs/subtitles-base/r3/report.md#z-001) |
| subtitles-base | По какому элементу экспортируемого формата приёмщик должен подтвердить, что для каждого поля временной метки объявлены миллисекунды? | Проверяемость | 2/3 | [2/Z-001](benchmark-runs/subtitles-base/r2/report.md#z-001), [3/Z-002](benchmark-runs/subtitles-base/r3/report.md#z-002) |
