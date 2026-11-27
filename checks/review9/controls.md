# Проверка таймера и двух соседних дефектов

Версия `af5d4e1`, модель `gpt-6.2-sol`. В изменённом варианте найдено **3 из 3** заложенных дефектов. Для согласованного текста число вопросов — **0**, число карточек — **0**. Строгая точность по паре — 3/3. [Штатная оценка](../finish/independent-runs/review9/evaluation.md) · [Предыдущая серия](../review8/controls.md)

| Размеченная проблема | Карточка |
|---|---|
| Выбор обязательной рамки | [Z-001](../finish/independent-runs/review9/case-p/report.md#z-001) |
| Результат для шестибайтовой метки | [Z-002](../finish/independent-runs/review9/case-p/report.md#z-002) |
| Предельное время полного цикла | [Z-003](../finish/independent-runs/review9/case-p/report.md#z-003) |

## Изменённый вариант

Число сверенных цитат — 36. Вызовы модели — 5. [Отчёт](../finish/independent-runs/review9/case-p/report.md) · [Паспорт](../finish/independent-runs/review9/case-p/report/run-meta.json)

**Какую из двух рамок контроллер обязан вывести при событии «Узор повреждён»?**

Тест из отчёта — Подать событие после сброса и сравнить показанную рамку с назначенной в П-1.

[Z-001](../finish/independent-runs/review9/case-p/report.md#z-001)

**Какое сообщение должен показать стенд для шестибайтовой метки «АБА»: «Отклонено» по М-1 или «Принято» по М-2?**

Тест из отчёта — После сброса один раз подать «АБА» и сверить сообщение стенда с результатом, согласованным в М-1 и М-2.

[Z-002](../finish/independent-runs/review9/case-p/report.md#z-002)

**Какой численный предел в миллисекундах применить к показанию таймера Э-1 и проходит ли показание, равное этому пределу?**

Тест из отчёта — Сравнить показание таймера с заданным пределом и применить правило для равенства.

[Z-003](../finish/independent-runs/review9/case-p/report.md#z-003)

[Попытка 1 (успех)](../finish/independent-cli/review9/case-p-attempt-1.txt)

## Согласованный вариант

Число сверенных цитат — 21. Вызовы модели — 4. [Отчёт](../finish/independent-runs/review9/case-p-base/report.md) · [Паспорт](../finish/independent-runs/review9/case-p-base/report/run-meta.json)

Очередь вопросов пуста. Границы измерения и предел 500 мс включительно указаны в исходнике. [Требования](../finish/independent/case-p/control.md#L16-L17) · [Очередь](../finish/independent-runs/review9/case-p-base/report.md#questions)

[Попытка 1 (успех)](../finish/independent-cli/review9/case-p-base-attempt-1.txt)

Оба документа и манифест совпадают с первоначальной фиксацией `1d3edbf`. Команда изучала результаты предыдущих запусков. [Разметка](../finish/independent/case-p/manifest.json)
