# Проверка таймера и двух соседних дефектов

Версия `7db8d3d`, модель `gpt-6.2-sol`. В изменённом варианте найдено **3 из 3** заложенных дефектов. Для согласованного текста число вопросов — **0**, число карточек — **0**. Строгая точность по паре — 3/3. [Штатная оценка](../finish/independent-runs/review10/evaluation.md) · [Предыдущая серия](../review9/controls.md)

| Размеченная проблема | Карточка |
|---|---|
| Выбор обязательной рамки | [Z-001](../finish/independent-runs/review10/case-p/report.md#z-001) |
| Результат для шестибайтовой метки | [Z-002](../finish/independent-runs/review10/case-p/report.md#z-002) |
| Предельное время полного цикла | [Z-003](../finish/independent-runs/review10/case-p/report.md#z-003) |

## Изменённый вариант

Число сверенных цитат — 30. Вызовы модели — 5. [Отчёт](../finish/independent-runs/review10/case-p/report.md) · [Паспорт](../finish/independent-runs/review10/case-p/report/run-meta.json)

**Какую рамку контроллер обязан вывести после события «Узор повреждён»: «точки» или «штрихи»?**

Тест из отчёта — После сброса один раз подать событие и проверить вывод выбранной рамки.

[Z-001](../finish/independent-runs/review10/case-p/report.md#z-001)

**Какой ответ должен показать стенд при входе «АБА» — «Отклонено» по М-1 или «Принято» по М-2?**

Тест из отчёта — После сброса один раз подать метку «АБА» длиной шесть байт в UTF-8 и проверить, что стенд показывает согласованный ответ.

[Z-002](../finish/independent-runs/review10/case-p/report.md#z-002)

**Какой предел в целых миллисекундах применять к показанию таймера и проходит ли опыт при равенстве этому пределу?**

Тест из отчёта — Сравнить показание общего таймера с заданным пределом и применить согласованный вердикт при равенстве.

[Z-003](../finish/independent-runs/review10/case-p/report.md#z-003)

[Попытка 1 (успех)](../finish/independent-cli/review10/case-p-attempt-1.txt)

## Согласованный вариант

Число сверенных цитат — 16. Вызовы модели — 4. [Отчёт](../finish/independent-runs/review10/case-p-base/report.md) · [Паспорт](../finish/independent-runs/review10/case-p-base/report/run-meta.json)

Очередь вопросов пуста. Границы измерения и предел 500 мс включительно указаны в исходнике. [Требования](../finish/independent/case-p/control.md#L16-L17) · [Очередь](../finish/independent-runs/review10/case-p-base/report.md#questions)

[Попытка 1 (успех)](../finish/independent-cli/review10/case-p-base-attempt-1.txt)

Оба документа и манифест совпадают с первоначальной фиксацией `1d3edbf`. Команда изучала результаты предыдущих запусков. [Разметка](../finish/independent/case-p/manifest.json)
