# Агент статического ревью требований

Агент читает Markdown, PDF с текстовым слоем или DOCX, сопоставляет требования и сохраняет русский отчёт с исходными цитатами. Модель — `gpt-6.2-sol` через Codex CLI.

После установки Python 3.10+, Git и Codex CLI выполните из корня проекта следующие команды.

```sh
python -m pip install -r requirements.txt
codex login
python -m requirements_validator --input docs/requirements.md --output .tmp/review.md
```
