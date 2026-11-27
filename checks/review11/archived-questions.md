# Сверка 17 записанных вопросов

Проверка формулировок и приёмочных тестов дала **17/17**. На предшествующем коде `7db8d3d` те же входы дали **16/17**. Использованы 17 исходных карточек и 127 утверждений из версии `5669ac8`. Вопросы и тесты для сравнения ранее выдала `gpt-6.2-sol` на версии `48f37df`. Обработан первый записанный ответ рецензента с единственной сохранённой правкой `/decisions/2/case_check`. [Исходные карточки](../../reports/finish4/review.md) · [Ответ и правка](../review8/fixed-queue-attempts/attempt-1.json) · [Вопросы после рецензии](../review8/fixed-queue.md)

В архивной Z-015 тест сначала воспроизводит четыре других отказа и проверяет применимость полей `result` и `enabled`. Затем отдельным запросом проверяет известное требование вернуть `result=ERROR` при отклонении суммы. Исправленный валидатор принимает обе части. Отдельно проверены три формулировки, в которых тестировщик лишь повторно читает тело, код или сообщение от того же запроса. Во всех трёх валидатор обнаружил потерю самостоятельного испытания. Полный локальный набор — **222/222**. [Регрессионные тесты](../../tests/test_response_representation.py)

По свободному отчёту предыдущей банковской проверки результат также воспроизведён на сохранённых данных. Валидатор принимает Z-015 о составе ответа при отклонении суммы и исходную формулировку Z-032 о применимости поля `enabled` при других отказах. Когда рецензент заменяет исходную Z-032 вторым вопросом про отклонённую сумму, валидатор требует вернуть решение об остальных отказах. [Карточка Z-015](../../reports/review9/review.md#z-015) · [Исходная строка матрицы](../../reports/review9/review/run-meta.json) · [Замена в Z-032](../../reports/review9/review.md#z-032)

Число 17/17 относится к повторному применению валидатора к известной очереди. Полнота извлечения тем при новом запуске банковского ТЗ измеряется отдельно. SHA-256 файла с записанными ответами — `e61d6ba50d77a59a96b411e9220a70ebe481deeed21c12fe152caf8b2d2cfc75`. SHA-256 проверенного модуля — `2a668b32831ce5bc8955f2f977a748d04c065cb650a8c2ca8b8eb0038d3f02c8`. [Проверенный модуль](../../requirements_validator/response_representation.py)

## Воспроизведение

В PowerShell из корня проекта следующая команда восстанавливает решения и сверяет все пары локально.

```powershell
@'
from pathlib import Path
import json, runpy
from requirements_validator import engine
from requirements_validator.response_representation import representation_error

folder = Path("checks/review8")
archive = runpy.run_path(str(folder / "fixed-queue-replay.py"))["archive"]
_, claims, candidates = archive(Path.cwd())
source = {claim["id"]: claim["quote"] for claim in claims}
record = json.loads((folder / "fixed-queue-attempts/attempt-1.json").read_bytes())
draft, repair = [step["response"] for step in record["responses"]]
final = engine._apply_patch(draft, engine.AUDIT, repair, ["/decisions/2"])
decisions = {item["id"]: item for item in final["decisions"]}
assert len(decisions) == len(candidates) == 17 and len(claims) == 127
for prior in candidates:
    current = engine._adjudicate_one(decisions[prior["id"]], prior, source)
    assert current and current["question"] and current["test"], prior["id"]
    assert not representation_error(current, prior, source), prior["id"]
print("17/17")
'@ | python -X utf8 -
```
