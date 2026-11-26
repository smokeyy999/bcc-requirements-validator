# Качество на размеченном корпусе

Дата оценки 2026-11-27T00:00:14+05:00. Провайдер и модель — OpenAI через Codex CLI · gpt-6.2-sol. Коммит реализации — `3018c8ee3c2868999c6070774331c57e0cb936ff`.

Основной результат измерен по первому запуску каждого документа. Полнота — **13/15 (86.7%)**. Точность — **13/24 (54.2%)**.

Во всех 3 прогонах воспроизвелось **12/44 (27.3%)** групп замечаний.

## Метод

Разметка и базовые версии не включаются в запросы модели. Балл даётся за точную категорию и пересечение цитат со всеми раздельно заданными диапазонами дефекта. Только одна пара «замечание — дефект» может получить балл. Конкурирующие пары и совпадения лишь по строкам остаются незачтёнными. Требования к совпадению зафиксированы до измерения. В знаменатель точности входят все опубликованные карточки Z, включая вопросы и рекомендации. Существование других реальных дефектов, включая контрольные документы, возможно. [Незачтённые замечания для проверки человеком](evaluation-manual.md)

Результаты dev и test приведены отдельно. Dev служит для разработки. Разметка test предназначена для измерения после фиксации механизма и не должна применяться для подбора подсказок.

| Часть | Прогон | Полнота | Точность |
|---|---:|---:|---:|
| all | 1 | 13/15 (86.7%) | 13/24 (54.2%) |
| all | 2 | 13/15 (86.7%) | 13/26 (50.0%) |
| all | 3 | 14/15 (93.3%) | 14/24 (58.3%) |
| dev | 1 | 4/5 (80.0%) | 4/6 (66.7%) |
| dev | 2 | 5/5 (100.0%) | 5/7 (71.4%) |
| dev | 3 | 5/5 (100.0%) | 5/7 (71.4%) |
| test | 1 | 9/10 (90.0%) | 9/18 (50.0%) |
| test | 2 | 8/10 (80.0%) | 8/19 (42.1%) |
| test | 3 | 9/10 (90.0%) | 9/17 (52.9%) |

## Типы дефектов

| Тип | Прогон | Найдено / заложено |
|---|---:|---:|
| дублирование с разными значениями | 1 | 1/1 (100.0%) |
| дублирование с разными значениями | 2 | 1/1 (100.0%) |
| дублирование с разными значениями | 3 | 1/1 (100.0%) |
| неопределённый термин | 1 | 0/1 (0.0%) |
| неопределённый термин | 2 | 0/1 (0.0%) |
| неопределённый термин | 3 | 1/1 (100.0%) |
| непроверяемое нефункциональное требование | 1 | 1/1 (100.0%) |
| непроверяемое нефункциональное требование | 2 | 1/1 (100.0%) |
| непроверяемое нефункциональное требование | 3 | 1/1 (100.0%) |
| несовпадение единиц | 1 | 2/2 (100.0%) |
| несовпадение единиц | 2 | 2/2 (100.0%) |
| несовпадение единиц | 3 | 1/2 (50.0%) |
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
| ссылка на несуществующий ID | 1 | 1/2 (50.0%) |
| ссылка на несуществующий ID | 2 | 2/2 (100.0%) |
| ссылка на несуществующий ID | 3 | 2/2 (100.0%) |

## Каждый эталон

| ТЗ / часть | ID | Тип | Категория | Строки | Дефект | Прогоны по порядку |
|---|---|---|---|---|---|---|
| dispatch / dev | D-01 | противоречие между правилами | Противоречивость | 6, 7 | Одна и та же ведомость в черновике одновременно допускается и запрещается к передаче. | [Z-001](benchmark-runs/dispatch/r1/report.md#z-001) · [Z-001](benchmark-runs/dispatch/r2/report.md#z-001) · [Z-001](benchmark-runs/dispatch/r3/report.md#z-001) |
| dispatch / dev | D-02 | разные числа для одного параметра | Противоречивость | 10, 11 | Файл из 25 строк принят при максимуме 24. | [Z-003](benchmark-runs/dispatch/r1/report.md#z-003) · [Z-002](benchmark-runs/dispatch/r2/report.md#z-002) · [Z-002](benchmark-runs/dispatch/r3/report.md#z-002) |
| dispatch / dev | D-03 | расплывчатый срок | Проверяемость | 12 | «Достаточно быстро» не задаёт предела для отображения результата. | [Z-004](benchmark-runs/dispatch/r1/report.md#z-004) · [Z-003](benchmark-runs/dispatch/r2/report.md#z-003) · [Z-006](benchmark-runs/dispatch/r3/report.md#z-006) |
| dispatch / dev | D-04 | ссылка на несуществующий ID | Трассируемость | 13 | Для сообщения об отказе указана отсутствующая норма S-97. | пропуск · [Z-004](benchmark-runs/dispatch/r2/report.md#z-004) · [Z-003](benchmark-runs/dispatch/r3/report.md#z-003) |
| dispatch / dev | D-05 | несовпадение единиц | Противоречивость | 15 | Один параметр измеряется в сутках, но его значение интерпретируется как часы. | [Z-006](benchmark-runs/dispatch/r1/report.md#z-006) · [Z-005](benchmark-runs/dispatch/r2/report.md#z-005) · [Z-004](benchmark-runs/dispatch/r3/report.md#z-004) |
| irrigation / test | I-01 | противоречие между правилами | Противоречивость | 6, 7 | Автоматика одновременно игнорирует команду и открывает клапан при ручной остановке. | [Z-003](benchmark-runs/irrigation/r1/report.md#z-003) · [Z-003](benchmark-runs/irrigation/r2/report.md#z-003) · [Z-003](benchmark-runs/irrigation/r3/report.md#z-003) |
| irrigation / test | I-02 | неопределённый термин | Ясность | 8 | Не определены признаки зоны категории омега. | пропуск · пропуск · [Z-005](benchmark-runs/irrigation/r3/report.md#z-005) |
| irrigation / test | I-03 | отсутствие обработки ошибки | Полнота | 9 | Документ требует аварийного положения клапана, но убрано указание, какое положение выбрать при некорректном датчике. | [Z-006](benchmark-runs/irrigation/r1/report.md#z-006) · пропуск · [Z-001](benchmark-runs/irrigation/r3/report.md#z-001) |
| irrigation / test | I-04 | отсутствие критерия приёмки | Полнота | 10 | Обязательному испытанию кнопки не заданы шаг и ожидаемый результат. | [Z-004](benchmark-runs/irrigation/r1/report.md#z-004) · [Z-004](benchmark-runs/irrigation/r2/report.md#z-004) · [Z-004](benchmark-runs/irrigation/r3/report.md#z-004) |
| irrigation / test | I-05 | дублирование с разными значениями | Противоречивость | 13, 14 | Для одной и той же повторной передачи предписаны три и пять повторов. | [Z-007](benchmark-runs/irrigation/r1/report.md#z-007) · [Z-008](benchmark-runs/irrigation/r2/report.md#z-008) · [Z-007](benchmark-runs/irrigation/r3/report.md#z-007) |
| subtitles / test | S-01 | противоречие между правилами | Противоречивость | 6, 7 | Маркер BOM одновременно обязателен и запрещён. | [Z-001](benchmark-runs/subtitles/r1/report.md#z-001) · [Z-001](benchmark-runs/subtitles/r2/report.md#z-001) · [Z-001](benchmark-runs/subtitles/r3/report.md#z-001) |
| subtitles / test | S-02 | несовпадение единиц | Противоречивость | 8 | 1000 мс названы одной минутой. | [Z-002](benchmark-runs/subtitles/r1/report.md#z-002) · [Z-002](benchmark-runs/subtitles/r2/report.md#z-002) · пропуск |
| subtitles / test | S-03 | непроверяемое нефункциональное требование | Проверяемость | 9 | Нет объективного способа принять «effortless to every user». | [Z-003](benchmark-runs/subtitles/r1/report.md#z-003) · [Z-003](benchmark-runs/subtitles/r2/report.md#z-003) · [Z-003](benchmark-runs/subtitles/r3/report.md#z-003) |
| subtitles / test | S-04 | ссылка на несуществующий ID | Трассируемость | 10 | Указан отсутствующий T-40 вместо существующего описания сообщения. | [Z-005](benchmark-runs/subtitles/r1/report.md#z-005) · [Z-005](benchmark-runs/subtitles/r2/report.md#z-005) · [Z-005](benchmark-runs/subtitles/r3/report.md#z-005) |
| subtitles / test | S-05 | разные числа для одного параметра | Противоречивость | 14, 15 | Тест принимает длину 81 при предельной длине 80. | [Z-004](benchmark-runs/subtitles/r1/report.md#z-004) · [Z-004](benchmark-runs/subtitles/r2/report.md#z-004) · [Z-004](benchmark-runs/subtitles/r3/report.md#z-004) |

## Сохранённые отчёты и контрольные документы

| Отчёт и прогон | Часть | Заложено | Замечаний | Зачтено |
|---|---|---:|---:|---:|
| [dispatch · 1](benchmark-runs/dispatch/r1/report.md) | dev | 5 | 5 | 4 |
| [dispatch · 2](benchmark-runs/dispatch/r2/report.md) | dev | 5 | 5 | 5 |
| [dispatch · 3](benchmark-runs/dispatch/r3/report.md) | dev | 5 | 5 | 5 |
| [dispatch-base · 1](benchmark-runs/dispatch-base/r1/report.md) | dev | 0 | 1 | 0 |
| [dispatch-base · 2](benchmark-runs/dispatch-base/r2/report.md) | dev | 0 | 2 | 0 |
| [dispatch-base · 3](benchmark-runs/dispatch-base/r3/report.md) | dev | 0 | 2 | 0 |
| [indicator · 1](benchmark-runs/indicator/r1/report.md) | test | 0 | 0 | 0 |
| [indicator · 2](benchmark-runs/indicator/r2/report.md) | test | 0 | 0 | 0 |
| [indicator · 3](benchmark-runs/indicator/r3/report.md) | test | 0 | 0 | 0 |
| [irrigation · 1](benchmark-runs/irrigation/r1/report.md) | test | 5 | 7 | 4 |
| [irrigation · 2](benchmark-runs/irrigation/r2/report.md) | test | 5 | 7 | 3 |
| [irrigation · 3](benchmark-runs/irrigation/r3/report.md) | test | 5 | 7 | 5 |
| [irrigation-base · 1](benchmark-runs/irrigation-base/r1/report.md) | test | 0 | 4 | 0 |
| [irrigation-base · 2](benchmark-runs/irrigation-base/r2/report.md) | test | 0 | 5 | 0 |
| [irrigation-base · 3](benchmark-runs/irrigation-base/r3/report.md) | test | 0 | 4 | 0 |
| [subtitles · 1](benchmark-runs/subtitles/r1/report.md) | test | 5 | 5 | 5 |
| [subtitles · 2](benchmark-runs/subtitles/r2/report.md) | test | 5 | 5 | 5 |
| [subtitles · 3](benchmark-runs/subtitles/r3/report.md) | test | 5 | 5 | 4 |
| [subtitles-base · 1](benchmark-runs/subtitles-base/r1/report.md) | test | 0 | 2 | 0 |
| [subtitles-base · 2](benchmark-runs/subtitles-base/r2/report.md) | test | 0 | 2 | 0 |
| [subtitles-base · 3](benchmark-runs/subtitles-base/r3/report.md) | test | 0 | 1 | 0 |

## Воспроизводимость замечаний

В одном документе сравниваются независимо полученные находки одной категории, у которых есть общая строка доказательства во всех вошедших прогонах и не более одного замечания в каждом. Конкурирующие или транзитивные совпадения показаны по отдельности и не дают балла устойчивости.

| ТЗ | Замечание | Категория | Частота | Прогон и ID |
|---|---|---|---:|---|
| dispatch | Отправка черновика | Противоречивость | 1/3 · спорное соответствие | [1/Z-001](benchmark-runs/dispatch/r1/report.md#z-001) |
| dispatch | Отправка ведомости с 25 строками груза | Противоречивость | 1/3 · спорное соответствие | [1/Z-003](benchmark-runs/dispatch/r1/report.md#z-003) |
| dispatch | Отправка черновика | Противоречивость | 1/3 · спорное соответствие | [2/Z-001](benchmark-runs/dispatch/r2/report.md#z-001) |
| dispatch | Отправка ведомости из 25 строк | Противоречивость | 1/3 · спорное соответствие | [2/Z-002](benchmark-runs/dispatch/r2/report.md#z-002) |
| dispatch | Отправка черновика | Противоречивость | 1/3 · спорное соответствие | [3/Z-001](benchmark-runs/dispatch/r3/report.md#z-001) |
| dispatch | Отправка ведомости из 25 строк | Противоречивость | 1/3 · спорное соответствие | [3/Z-002](benchmark-runs/dispatch/r3/report.md#z-002) |
| dispatch | Задержка отображения подтверждения | Проверяемость | 3/3 | [1/Z-004](benchmark-runs/dispatch/r1/report.md#z-004), [2/Z-003](benchmark-runs/dispatch/r2/report.md#z-003), [3/Z-006](benchmark-runs/dispatch/r3/report.md#z-006) |
| dispatch | Какое правило вывода текста при отказе имеет в виду S-6 — правило S-7 или отдельное правило, совместимое с S-7? | Полнота | 1/3 | [1/Z-005](benchmark-runs/dispatch/r1/report.md#z-005) |
| dispatch | Срок хранения при значении 7 | Противоречивость | 3/3 | [1/Z-006](benchmark-runs/dispatch/r1/report.md#z-006), [2/Z-005](benchmark-runs/dispatch/r2/report.md#z-005), [3/Z-004](benchmark-runs/dispatch/r3/report.md#z-004) |
| dispatch | Отсутствующее правило текста отказа | Трассируемость | 2/3 | [2/Z-004](benchmark-runs/dispatch/r2/report.md#z-004), [3/Z-003](benchmark-runs/dispatch/r3/report.md#z-003) |
| dispatch-base | Три секунды для сообщения «Передано» | Однозначность | 3/3 | [1/Z-001](benchmark-runs/dispatch-base/r1/report.md#z-001), [2/Z-001](benchmark-runs/dispatch-base/r2/report.md#z-001), [3/Z-001](benchmark-runs/dispatch-base/r3/report.md#z-001) |
| dispatch-base | Достаточно ли при приёмке наблюдать отказ в загрузке ведомости из 25 строк, чтобы подтвердить причину «слишком большой», или причину нужно наблюдать отдельно? | Полнота | 1/3 | [2/Z-002](benchmark-runs/dispatch-base/r2/report.md#z-002) |
| dispatch-base | От какого события отсчитываются семь суток локального хранения при настройке 7, если терминал получил подтверждение перевозчика раньше, чем сохранил его локально? | Полнота | 1/3 | [3/Z-002](benchmark-runs/dispatch-base/r3/report.md#z-002) |
| irrigation | Какое действие должен выполнить контроллер при допустимом показании влажности с учётом текущего состояния полива, если ручная остановка снята? | Полнота | 1/3 | [1/Z-001](benchmark-runs/irrigation/r1/report.md#z-001) |
| irrigation | Какое значение должна получить панель при повторе после первого таймаута и по каким исходным данным определить это значение? | Полнота | 3/3 | [1/Z-002](benchmark-runs/irrigation/r1/report.md#z-002), [2/Z-002](benchmark-runs/irrigation/r2/report.md#z-002), [3/Z-002](benchmark-runs/irrigation/r3/report.md#z-002) |
| irrigation | Команда расписания при ручной остановке | Противоречивость | 3/3 | [1/Z-003](benchmark-runs/irrigation/r1/report.md#z-003), [2/Z-003](benchmark-runs/irrigation/r2/report.md#z-003), [3/Z-003](benchmark-runs/irrigation/r3/report.md#z-003) |
| irrigation | Состав испытания кнопки «Возобновить» | Полнота | 3/3 | [1/Z-004](benchmark-runs/irrigation/r1/report.md#z-004), [2/Z-004](benchmark-runs/irrigation/r2/report.md#z-004), [3/Z-004](benchmark-runs/irrigation/r3/report.md#z-004) |
| irrigation | По какому признаку или перечню определить принадлежность зоны к категории «омега»? | Полнота | 2/3 | [1/Z-005](benchmark-runs/irrigation/r1/report.md#z-005), [2/Z-006](benchmark-runs/irrigation/r2/report.md#z-006) |
| irrigation | Условие и результат аварийного перехода | Полнота | 1/3 · спорное соответствие | [1/Z-006](benchmark-runs/irrigation/r1/report.md#z-006) |
| irrigation | По какому правилу контроллер должен распознавать некорректное показание датчика влажности? | Полнота | 1/3 · спорное соответствие | [2/Z-001](benchmark-runs/irrigation/r2/report.md#z-001) |
| irrigation | Аварийное положение клапана | Полнота | 1/3 · спорное соответствие | [2/Z-007](benchmark-runs/irrigation/r2/report.md#z-007) |
| irrigation | По какому критерию контроллер должен считать показание датчика влажности некорректным? | Полнота | 1/3 · спорное соответствие | [3/Z-001](benchmark-runs/irrigation/r3/report.md#z-001) |
| irrigation | Число повторных передач | Противоречивость | 3/3 | [1/Z-007](benchmark-runs/irrigation/r1/report.md#z-007), [2/Z-008](benchmark-runs/irrigation/r2/report.md#z-008), [3/Z-007](benchmark-runs/irrigation/r3/report.md#z-007) |
| irrigation | Категория зоны «омега» | Ясность | 1/3 | [3/Z-005](benchmark-runs/irrigation/r3/report.md#z-005) |
| irrigation | Ссылка на аварийное положение клапана | Трассируемость | 1/3 | [3/Z-006](benchmark-runs/irrigation/r3/report.md#z-006) |
| irrigation-base | Какое значение контроллер должен передавать на панель и по какому исходному значению его сверять? | Полнота | 3/3 | [1/Z-001](benchmark-runs/irrigation-base/r1/report.md#z-001), [2/Z-001](benchmark-runs/irrigation-base/r2/report.md#z-001), [3/Z-003](benchmark-runs/irrigation-base/r3/report.md#z-003) |
| irrigation-base | По каким признакам контроллер должен считать полученное показание влажности некорректным для срабатывания W-4? | Проверяемость | 1/3 | [1/Z-002](benchmark-runs/irrigation-base/r1/report.md#z-002) |
| irrigation-base | Как корректное показание влажности влияет на открытие закрытого клапана при выбранной зоне, вне ручной остановки и без команды расписания? | Полнота | 1/3 · спорное соответствие | [1/Z-003](benchmark-runs/irrigation-base/r1/report.md#z-003) |
| irrigation-base | В какое положение должно перевести уже открытый клапан само нажатие ручной остановки при отсутствии других событий? | Полнота | 1/3 · спорное соответствие | [1/Z-004](benchmark-runs/irrigation-base/r1/report.md#z-004) |
| irrigation-base | Какое действие должен выполнить контроллер для каждого случая штатной влажности при включённой автоматике и выбранной зоне? | Полнота | 1/3 · спорное соответствие | [2/Z-002](benchmark-runs/irrigation-base/r2/report.md#z-002) |
| irrigation-base | Какое положение должен занять уже открытый клапан в результате самого нажатия кнопки ручной остановки? | Полнота | 1/3 · спорное соответствие | [2/Z-003](benchmark-runs/irrigation-base/r2/report.md#z-003) |
| irrigation-base | По какому правилу контроллер решает, запускать ли полив выбранной зоны при корректных показаниях влажности? | Полнота | 1/3 · спорное соответствие | [3/Z-001](benchmark-runs/irrigation-base/r3/report.md#z-001) |
| irrigation-base | Должен ли уже открытый клапан закрыться при нажатии кнопки ручной остановки? | Полнота | 1/3 · спорное соответствие | [3/Z-004](benchmark-runs/irrigation-base/r3/report.md#z-004) |
| irrigation-base | По какому критерию полученное значение датчика относится к некорректным для W-4? | Полнота | 2/3 | [2/Z-004](benchmark-runs/irrigation-base/r2/report.md#z-004), [3/Z-002](benchmark-runs/irrigation-base/r3/report.md#z-002) |
| irrigation-base | Дублирование числа повторов | Дублирование | 1/3 | [2/Z-005](benchmark-runs/irrigation-base/r2/report.md#z-005) |
| subtitles | BOM в начале файла | Противоречивость | 3/3 | [1/Z-001](benchmark-runs/subtitles/r1/report.md#z-001), [2/Z-001](benchmark-runs/subtitles/r2/report.md#z-001), [3/Z-001](benchmark-runs/subtitles/r3/report.md#z-001) |
| subtitles | Шкала временных меток | Противоречивость | 2/3 | [1/Z-002](benchmark-runs/subtitles/r1/report.md#z-002), [2/Z-002](benchmark-runs/subtitles/r2/report.md#z-002) |
| subtitles | Критерий простоты экспорта | Проверяемость | 3/3 | [1/Z-003](benchmark-runs/subtitles/r1/report.md#z-003), [2/Z-003](benchmark-runs/subtitles/r2/report.md#z-003), [3/Z-003](benchmark-runs/subtitles/r3/report.md#z-003) |
| subtitles | Реплика из 81 кодовой точки | Противоречивость | 3/3 | [1/Z-004](benchmark-runs/subtitles/r1/report.md#z-004), [2/Z-004](benchmark-runs/subtitles/r2/report.md#z-004), [3/Z-004](benchmark-runs/subtitles/r3/report.md#z-004) |
| subtitles | Битая ссылка на текст сообщения | Трассируемость | 3/3 | [1/Z-005](benchmark-runs/subtitles/r1/report.md#z-005), [2/Z-005](benchmark-runs/subtitles/r2/report.md#z-005), [3/Z-005](benchmark-runs/subtitles/r3/report.md#z-005) |
| subtitles | Что означает объявление миллисекунд в T-3 при заданном соответствии 1000 одной минуте — единицу записанного числа или обозначение шкалы поля с отдельным правилом кодирования? | Полнота | 1/3 | [3/Z-002](benchmark-runs/subtitles/r3/report.md#z-002) |
| subtitles-base | Результат отклонения субтитра | Полнота | 2/3 | [1/Z-001](benchmark-runs/subtitles-base/r1/report.md#z-001), [3/Z-001](benchmark-runs/subtitles-base/r3/report.md#z-001) |
| subtitles-base | Объявление единицы временной метки | Проверяемость | 2/3 | [1/Z-002](benchmark-runs/subtitles-base/r1/report.md#z-002), [2/Z-002](benchmark-runs/subtitles-base/r2/report.md#z-002) |
| subtitles-base | Область отклонения длинной реплики | Однозначность | 1/3 | [2/Z-001](benchmark-runs/subtitles-base/r2/report.md#z-001) |
