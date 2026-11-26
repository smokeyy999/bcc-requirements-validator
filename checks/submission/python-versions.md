# Автономные тесты под Windows

Коммит `9869df2a2dec652ec20a1cf6e77ac66ed3eda4e5`. Каждый интерпретатор импортировал пакет из чистого клона, выполнил один и тот же набор тестов и команду справки CLI.

| CPython x64 | Успешных тестов | Секунды | Код выхода --help |
|---|---:|---:|---:|
| 3.10.11 | 84 | 0.863 | 0 |
| 3.12.14 | 84 | 0.839 | 0 |
| 3.15.2 | 84 | 0.936 | 0 |

[Установка в новом окружении](reproduction.txt) · [CPython 3.10.11](https://www.python.org/downloads/release/python-31011/) · [CPython 3.15.2](https://www.python.org/downloads/release/python-3152/)
