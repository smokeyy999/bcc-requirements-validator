# Качество на размеченном корпусе

Дата оценки 2026-11-27T00:08:12+05:00. Провайдер и модель — OpenAI через Codex CLI · gpt-6.2-sol. Коммит реализации — `31ea961359915ef65910eddd2ea750d37ccefc57`.

Основной результат измерен по первому запуску каждого документа. Полнота — **12/15 (80.0%)**. Точность — **12/23 (52.2%)**.

Во всех 3 прогонах воспроизвелось **13/46 (28.3%)** групп замечаний.

## Метод

Разметка и базовые версии не включаются в запросы модели. Балл даётся за точную категорию и пересечение цитат со всеми раздельно заданными диапазонами дефекта. Только одна пара «замечание — дефект» может получить балл. Конкурирующие пары и совпадения лишь по строкам остаются незачтёнными. Требования к совпадению зафиксированы до измерения. В знаменатель точности входят все опубликованные карточки Z, включая вопросы и рекомендации. Существование других реальных дефектов, включая контрольные документы, возможно. [Незачтённые замечания для проверки человеком](evaluation-manual.md)

Результаты dev и test приведены отдельно. Dev служит для разработки. Разметка test предназначена для измерения после фиксации механизма и не должна применяться для подбора подсказок.

| Часть | Прогон | Полнота | Точность |
|---|---:|---:|---:|
| all | 1 | 12/15 (80.0%) | 12/23 (52.2%) |
| all | 2 | 13/15 (86.7%) | 13/27 (48.1%) |
| all | 3 | 14/15 (93.3%) | 14/26 (53.8%) |
| dev | 1 | 4/5 (80.0%) | 4/6 (66.7%) |
| dev | 2 | 5/5 (100.0%) | 5/6 (83.3%) |
| dev | 3 | 5/5 (100.0%) | 5/7 (71.4%) |
| test | 1 | 8/10 (80.0%) | 8/17 (47.1%) |
| test | 2 | 8/10 (80.0%) | 8/21 (38.1%) |
| test | 3 | 9/10 (90.0%) | 9/19 (47.4%) |

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
| отсутствие критерия приёмки | 3 | 1/1 (100.0%) |
| отсутствие обработки ошибки | 1 | 0/1 (0.0%) |
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
| dispatch / dev | D-02 | разные числа для одного параметра | Противоречивость | 10, 11 | Файл из 25 строк принят при максимуме 24. | [Z-002](benchmark-runs/dispatch/r1/report.md#z-002) · [Z-002](benchmark-runs/dispatch/r2/report.md#z-002) · [Z-002](benchmark-runs/dispatch/r3/report.md#z-002) |
| dispatch / dev | D-03 | расплывчатый срок | Проверяемость | 12 | «Достаточно быстро» не задаёт предела для отображения результата. | [Z-005](benchmark-runs/dispatch/r1/report.md#z-005) · [Z-003](benchmark-runs/dispatch/r2/report.md#z-003) · [Z-003](benchmark-runs/dispatch/r3/report.md#z-003) |
| dispatch / dev | D-04 | ссылка на несуществующий ID | Трассируемость | 13 | Для сообщения об отказе указана отсутствующая норма S-97. | пропуск · [Z-006](benchmark-runs/dispatch/r2/report.md#z-006) · [Z-006](benchmark-runs/dispatch/r3/report.md#z-006) |
| dispatch / dev | D-05 | несовпадение единиц | Противоречивость | 15 | Один параметр измеряется в сутках, но его значение интерпретируется как часы. | [Z-003](benchmark-runs/dispatch/r1/report.md#z-003) · [Z-004](benchmark-runs/dispatch/r2/report.md#z-004) · [Z-004](benchmark-runs/dispatch/r3/report.md#z-004) |
| irrigation / test | I-01 | противоречие между правилами | Противоречивость | 6, 7 | Автоматика одновременно игнорирует команду и открывает клапан при ручной остановке. | [Z-004](benchmark-runs/irrigation/r1/report.md#z-004) · [Z-005](benchmark-runs/irrigation/r2/report.md#z-005) · [Z-003](benchmark-runs/irrigation/r3/report.md#z-003) |
| irrigation / test | I-02 | неопределённый термин | Ясность | 8 | Не определены признаки зоны категории омега. | пропуск · пропуск · пропуск |
| irrigation / test | I-03 | отсутствие обработки ошибки | Полнота | 9 | Документ требует аварийного положения клапана, но убрано указание, какое положение выбрать при некорректном датчике. | пропуск · пропуск · [Z-001](benchmark-runs/irrigation/r3/report.md#z-001) |
| irrigation / test | I-04 | отсутствие критерия приёмки | Полнота | 10 | Обязательному испытанию кнопки не заданы шаг и ожидаемый результат. | [Z-005](benchmark-runs/irrigation/r1/report.md#z-005) · [Z-006](benchmark-runs/irrigation/r2/report.md#z-006) · [Z-004](benchmark-runs/irrigation/r3/report.md#z-004) |
| irrigation / test | I-05 | дублирование с разными значениями | Противоречивость | 13, 14 | Для одной и той же повторной передачи предписаны три и пять повторов. | [Z-009](benchmark-runs/irrigation/r1/report.md#z-009) · [Z-009](benchmark-runs/irrigation/r2/report.md#z-009) · [Z-007](benchmark-runs/irrigation/r3/report.md#z-007) |
| subtitles / test | S-01 | противоречие между правилами | Противоречивость | 6, 7 | Маркер BOM одновременно обязателен и запрещён. | [Z-001](benchmark-runs/subtitles/r1/report.md#z-001) · [Z-001](benchmark-runs/subtitles/r2/report.md#z-001) · [Z-001](benchmark-runs/subtitles/r3/report.md#z-001) |
| subtitles / test | S-02 | несовпадение единиц | Противоречивость | 8 | 1000 мс названы одной минутой. | [Z-002](benchmark-runs/subtitles/r1/report.md#z-002) · [Z-002](benchmark-runs/subtitles/r2/report.md#z-002) · [Z-002](benchmark-runs/subtitles/r3/report.md#z-002) |
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
| [dispatch-base · 2](benchmark-runs/dispatch-base/r2/report.md) | dev | 0 | 1 | 0 |
| [dispatch-base · 3](benchmark-runs/dispatch-base/r3/report.md) | dev | 0 | 2 | 0 |
| [indicator · 1](benchmark-runs/indicator/r1/report.md) | test | 0 | 0 | 0 |
| [indicator · 2](benchmark-runs/indicator/r2/report.md) | test | 0 | 0 | 0 |
| [indicator · 3](benchmark-runs/indicator/r3/report.md) | test | 0 | 0 | 0 |
| [irrigation · 1](benchmark-runs/irrigation/r1/report.md) | test | 5 | 8 | 3 |
| [irrigation · 2](benchmark-runs/irrigation/r2/report.md) | test | 5 | 9 | 3 |
| [irrigation · 3](benchmark-runs/irrigation/r3/report.md) | test | 5 | 6 | 4 |
| [irrigation-base · 1](benchmark-runs/irrigation-base/r1/report.md) | test | 0 | 4 | 0 |
| [irrigation-base · 2](benchmark-runs/irrigation-base/r2/report.md) | test | 0 | 5 | 0 |
| [irrigation-base · 3](benchmark-runs/irrigation-base/r3/report.md) | test | 0 | 5 | 0 |
| [subtitles · 1](benchmark-runs/subtitles/r1/report.md) | test | 5 | 5 | 5 |
| [subtitles · 2](benchmark-runs/subtitles/r2/report.md) | test | 5 | 5 | 5 |
| [subtitles · 3](benchmark-runs/subtitles/r3/report.md) | test | 5 | 5 | 5 |
| [subtitles-base · 1](benchmark-runs/subtitles-base/r1/report.md) | test | 0 | 0 | 0 |
| [subtitles-base · 2](benchmark-runs/subtitles-base/r2/report.md) | test | 0 | 2 | 0 |
| [subtitles-base · 3](benchmark-runs/subtitles-base/r3/report.md) | test | 0 | 3 | 0 |

## Воспроизводимость замечаний

В одном документе сравниваются независимо полученные находки одной категории, у которых есть общая строка доказательства во всех вошедших прогонах и не более одного замечания в каждом. Конкурирующие или транзитивные совпадения показаны по отдельности и не дают балла устойчивости.

| ТЗ | Замечание | Категория | Частота | Прогон и ID |
|---|---|---|---:|---|
| dispatch | Отправка черновика | Противоречивость | 1/3 · спорное соответствие | [1/Z-001](benchmark-runs/dispatch/r1/report.md#z-001) |
| dispatch | Допуск к отправке 25 строк | Противоречивость | 1/3 · спорное соответствие | [1/Z-002](benchmark-runs/dispatch/r1/report.md#z-002) |
| dispatch | Отправка черновика | Противоречивость | 1/3 · спорное соответствие | [2/Z-001](benchmark-runs/dispatch/r2/report.md#z-001) |
| dispatch | Отправка ведомости из 25 строк | Противоречивость | 1/3 · спорное соответствие | [2/Z-002](benchmark-runs/dispatch/r2/report.md#z-002) |
| dispatch | Отправка черновика | Противоречивость | 1/3 · спорное соответствие | [3/Z-001](benchmark-runs/dispatch/r3/report.md#z-001) |
| dispatch | Отправка ведомости из 25 строк | Противоречивость | 1/3 · спорное соответствие | [3/Z-002](benchmark-runs/dispatch/r3/report.md#z-002) |
| dispatch | Единица срока хранения | Противоречивость | 3/3 | [1/Z-003](benchmark-runs/dispatch/r1/report.md#z-003), [2/Z-004](benchmark-runs/dispatch/r2/report.md#z-004), [3/Z-004](benchmark-runs/dispatch/r3/report.md#z-004) |
| dispatch | Время показа подтверждения | Проверяемость | 3/3 | [1/Z-005](benchmark-runs/dispatch/r1/report.md#z-005), [2/Z-003](benchmark-runs/dispatch/r2/report.md#z-003), [3/Z-003](benchmark-runs/dispatch/r3/report.md#z-003) |
| dispatch | Достаточно ли для выполнения S-6 показать «Передача отклонена» по S-7 или при том же отказе действует дополнительное правило вывода текста? | Полнота | 1/3 | [1/Z-006](benchmark-runs/dispatch/r1/report.md#z-006) |
| dispatch | Ссылка на правило сообщения об отказе | Трассируемость | 2/3 | [2/Z-006](benchmark-runs/dispatch/r2/report.md#z-006), [3/Z-006](benchmark-runs/dispatch/r3/report.md#z-006) |
| dispatch-base | Три секунды для показа «Передано» | Однозначность | 3/3 | [1/Z-001](benchmark-runs/dispatch-base/r1/report.md#z-001), [2/Z-001](benchmark-runs/dispatch-base/r2/report.md#z-001), [3/Z-001](benchmark-runs/dispatch-base/r3/report.md#z-001) |
| dispatch-base | Какое событие запускает отсчёт срока локального хранения подтверждения перевозчика? | Полнота | 1/3 | [3/Z-002](benchmark-runs/dispatch-base/r3/report.md#z-002) |
| irrigation | Какое действие контроллера ожидается для корректного показания влажности с учётом исходного положения клапана, когда ручная остановка выключена и команды расписания нет? | Полнота | 1/3 · спорное соответствие | [1/Z-001](benchmark-runs/irrigation/r1/report.md#z-001) |
| irrigation | По какому правилу полученное значение датчика считается некорректным для применения W-4? | Полнота | 1/3 · спорное соответствие | [1/Z-002](benchmark-runs/irrigation/r1/report.md#z-002) |
| irrigation | Приёмочное испытание кнопки «Возобновить» | Полнота | 1/3 · спорное соответствие | [1/Z-005](benchmark-runs/irrigation/r1/report.md#z-005) |
| irrigation | Аварийное положение клапана | Полнота | 1/3 · спорное соответствие | [1/Z-008](benchmark-runs/irrigation/r1/report.md#z-008) |
| irrigation | Как корректные показания влажности определяют, откроется ли закрытый клапан при снятой ручной остановке и без команды расписания? | Полнота | 1/3 · спорное соответствие | [2/Z-001](benchmark-runs/irrigation/r2/report.md#z-001) |
| irrigation | По какому критерию контроллер признаёт показание датчика влажности некорректным для применения W-4? | Полнота | 1/3 · спорное соответствие | [2/Z-002](benchmark-runs/irrigation/r2/report.md#z-002) |
| irrigation | Какое положение должен занять уже открытый клапан после нажатия ручной остановки при отсутствии новых команд открытия? | Полнота | 1/3 · спорное соответствие | [2/Z-004](benchmark-runs/irrigation/r2/report.md#z-004) |
| irrigation | Приёмка кнопки «Возобновить» | Полнота | 1/3 · спорное соответствие | [2/Z-006](benchmark-runs/irrigation/r2/report.md#z-006) |
| irrigation | Аварийное положение клапана | Полнота | 1/3 · спорное соответствие | [2/Z-008](benchmark-runs/irrigation/r2/report.md#z-008) |
| irrigation | Вход и результат аварийного сценария | Полнота | 1/3 · спорное соответствие | [3/Z-001](benchmark-runs/irrigation/r3/report.md#z-001) |
| irrigation | Приёмочное испытание кнопки «Возобновить» | Полнота | 1/3 · спорное соответствие | [3/Z-004](benchmark-runs/irrigation/r3/report.md#z-004) |
| irrigation | Из каких данных и по какому правилу определить ожидаемое значение в повторной передаче на панель? | Полнота | 3/3 | [1/Z-003](benchmark-runs/irrigation/r1/report.md#z-003), [2/Z-003](benchmark-runs/irrigation/r2/report.md#z-003), [3/Z-002](benchmark-runs/irrigation/r3/report.md#z-002) |
| irrigation | Ответ на команду расписания при ручной остановке | Противоречивость | 3/3 | [1/Z-004](benchmark-runs/irrigation/r1/report.md#z-004), [2/Z-005](benchmark-runs/irrigation/r2/report.md#z-005), [3/Z-003](benchmark-runs/irrigation/r3/report.md#z-003) |
| irrigation | По какому критерию определить, относится ли включённая зона к категории «омега»? | Полнота | 3/3 | [1/Z-007](benchmark-runs/irrigation/r1/report.md#z-007), [2/Z-007](benchmark-runs/irrigation/r2/report.md#z-007), [3/Z-006](benchmark-runs/irrigation/r3/report.md#z-006) |
| irrigation | Число повторов передачи после таймаута | Противоречивость | 3/3 | [1/Z-009](benchmark-runs/irrigation/r1/report.md#z-009), [2/Z-009](benchmark-runs/irrigation/r2/report.md#z-009), [3/Z-007](benchmark-runs/irrigation/r3/report.md#z-007) |
| irrigation-base | По какому правилу корректное показание влажности определяет действие клапана выбранной зоны в обычном режиме? | Полнота | 1/3 · спорное соответствие | [1/Z-001](benchmark-runs/irrigation-base/r1/report.md#z-001) |
| irrigation-base | Какое положение должен занять открытый клапан при нажатии ручной остановки во время полива, до поступления других команд? | Полнота | 1/3 · спорное соответствие | [1/Z-004](benchmark-runs/irrigation-base/r1/report.md#z-004) |
| irrigation-base | Как должна меняться позиция клапана выбранной зоны по корректным показаниям влажности при выключенной ручной остановке? | Полнота | 1/3 · спорное соответствие | [2/Z-001](benchmark-runs/irrigation-base/r2/report.md#z-001) |
| irrigation-base | В каком положении должен оказаться уже открытый клапан после нажатия кнопки ручной остановки, если новых команд нет? | Полнота | 1/3 · спорное соответствие | [2/Z-003](benchmark-runs/irrigation-base/r2/report.md#z-003) |
| irrigation-base | При каких корректных показаниях влажности контроллер должен открыть закрытый клапан выбранной зоны, если ручная остановка не действует и команды расписания нет? | Полнота | 1/3 · спорное соответствие | [3/Z-001](benchmark-runs/irrigation-base/r3/report.md#z-001) |
| irrigation-base | Какое положение должен занять уже открытый клапан после нажатия ручной остановки, если новых команд и показаний нет? | Полнота | 1/3 · спорное соответствие | [3/Z-003](benchmark-runs/irrigation-base/r3/report.md#z-003) |
| irrigation-base | По какому критерию полученное показание датчика считается некорректным для применения W-4? | Полнота | 2/3 | [1/Z-002](benchmark-runs/irrigation-base/r1/report.md#z-002), [2/Z-004](benchmark-runs/irrigation-base/r2/report.md#z-004) |
| irrigation-base | Из каких исходных данных определяется значение, которое контроллер передаёт на панель? | Полнота | 3/3 | [1/Z-003](benchmark-runs/irrigation-base/r1/report.md#z-003), [2/Z-002](benchmark-runs/irrigation-base/r2/report.md#z-002), [3/Z-002](benchmark-runs/irrigation-base/r3/report.md#z-002) |
| irrigation-base | Дублирование числа повторов | Дублирование | 2/3 | [2/Z-005](benchmark-runs/irrigation-base/r2/report.md#z-005), [3/Z-005](benchmark-runs/irrigation-base/r3/report.md#z-005) |
| irrigation-base | По каким критериям показание датчика считается некорректным для срабатывания W-4? | Проверяемость | 1/3 | [3/Z-004](benchmark-runs/irrigation-base/r3/report.md#z-004) |
| subtitles | BOM в файле экспорта | Противоречивость | 3/3 | [1/Z-001](benchmark-runs/subtitles/r1/report.md#z-001), [2/Z-001](benchmark-runs/subtitles/r2/report.md#z-001), [3/Z-001](benchmark-runs/subtitles/r3/report.md#z-001) |
| subtitles | Шкала временных меток | Противоречивость | 3/3 | [1/Z-002](benchmark-runs/subtitles/r1/report.md#z-002), [2/Z-002](benchmark-runs/subtitles/r2/report.md#z-002), [3/Z-002](benchmark-runs/subtitles/r3/report.md#z-002) |
| subtitles | Критерий лёгкости экспорта | Проверяемость | 3/3 | [1/Z-003](benchmark-runs/subtitles/r1/report.md#z-003), [2/Z-003](benchmark-runs/subtitles/r2/report.md#z-003), [3/Z-003](benchmark-runs/subtitles/r3/report.md#z-003) |
| subtitles | Приёмка реплики из 81 кодовой точки | Противоречивость | 3/3 | [1/Z-004](benchmark-runs/subtitles/r1/report.md#z-004), [2/Z-004](benchmark-runs/subtitles/r2/report.md#z-004), [3/Z-004](benchmark-runs/subtitles/r3/report.md#z-004) |
| subtitles | Ссылка на сообщение о пустой дорожке | Трассируемость | 3/3 | [1/Z-005](benchmark-runs/subtitles/r1/report.md#z-005), [2/Z-005](benchmark-runs/subtitles/r2/report.md#z-005), [3/Z-005](benchmark-runs/subtitles/r3/report.md#z-005) |
| subtitles-base | Каков ожидаемый исход команды экспорта в существующий файл, если одна реплика допустима, а другая подлежит отклонению? | Полнота | 1/3 · спорное соответствие | [2/Z-001](benchmark-runs/subtitles-base/r2/report.md#z-001) |
| subtitles-base | Из какого источника приёмочный тест определяет локальный путь назначения конкретного вызова экспорта, включая вызов для пустой дорожки? | Полнота | 1/3 · спорное соответствие | [3/Z-002](benchmark-runs/subtitles-base/r3/report.md#z-002) |
| subtitles-base | Наблюдаемый результат отклонения реплики | Полнота | 1/3 · спорное соответствие | [3/Z-004](benchmark-runs/subtitles-base/r3/report.md#z-004) |
| subtitles-base | Где и по какому признаку проверяющий должен распознать объявление миллисекунд для каждого поля временной метки? | Проверяемость | 2/3 | [2/Z-002](benchmark-runs/subtitles-base/r2/report.md#z-002), [3/Z-003](benchmark-runs/subtitles-base/r3/report.md#z-003) |
