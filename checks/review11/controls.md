# Проверка таймера и двух соседних дефектов

Версия `05ef616`, модель `gpt-6.2-sol`. В изменённом варианте найдено **3 из 3** заложенных дефектов. Для согласованного текста число вопросов — **0**, число карточек — **0**. Строгая точность по паре — 3/3. [Штатная оценка](../finish/independent-runs/review11/evaluation.md) · [Предыдущая серия](../review10/controls.md)

| Размеченная проблема | Карточка |
|---|---|
| Выбор обязательной рамки | [Z-001](../finish/independent-runs/review11/case-p/report.md#z-001) |
| Результат для шестибайтовой метки | [Z-002](../finish/independent-runs/review11/case-p/report.md#z-002) |
| Предельное время полного цикла | [Z-003](../finish/independent-runs/review11/case-p/report.md#z-003) |

## Изменённый вариант

Число сверенных цитат — 32. Вызовы модели — 4. [Отчёт](../finish/independent-runs/review11/case-p/report.md) · [Паспорт](../finish/independent-runs/review11/case-p/report/run-meta.json)

**Контроллер обязан вывести рамку. Какая рамка назначена событию «Узор повреждён», «точки» или «штрихи»?**

Тест из отчёта — Подать событие после сброса и проверить, что контроллер вывел назначенную рамку.

[Z-001](../finish/independent-runs/review11/case-p/report.md#z-001)

**Какой результат принять для «АБА», «Отклонено» по общему порогу или «Принято» как явное исключение?**

Тест из отчёта — После сброса один раз подать «АБА» и сравнить показанный ответ с выбранным результатом.

[Z-002](../finish/independent-runs/review11/case-p/report.md#z-002)

**Какой предел в целых миллисекундах применить к показанию таймера по Э-1 и проходит ли опыт при равенстве пределу?**

Тест из отчёта — Сравнить показание таймера полного цикла с заданным пределом и применить согласованное правило при равенстве.

[Z-003](../finish/independent-runs/review11/case-p/report.md#z-003)

[Попытка 1 (успех)](../finish/independent-cli/review11/case-p-attempt-1.txt)

## Согласованный вариант

Число сверенных цитат — 20. Вызовы модели — 4. [Отчёт](../finish/independent-runs/review11/case-p-base/report.md) · [Паспорт](../finish/independent-runs/review11/case-p-base/report/run-meta.json)

Очередь вопросов пуста. Границы измерения и предел 500 мс включительно указаны в исходнике. [Требования](../finish/independent/case-p/control.md#L16-L17) · [Очередь](../finish/independent-runs/review11/case-p-base/report.md#questions)

[Попытка 1 (успех)](../finish/independent-cli/review11/case-p-base-attempt-1.txt)

Оба документа и манифест совпадают с первоначальной фиксацией `1d3edbf`. Команда изучала результаты предыдущих запусков. [Разметка](../finish/independent/case-p/manifest.json)
