# Автономные тесты под Windows

Коммит `debbf8554fe6e4105e75c0a4addf218a4dfb20b6`. Каждый интерпретатор импортировал пакет из чистого клона, выполнил один и тот же набор тестов и команду справки CLI.

| CPython x64 | Успешных тестов | Секунды | Код выхода --help |
|---|---:|---:|---:|
| 3.10.11 | 79 | 0.952 | 0 |
| 3.12.14 | 79 | 1.000 | 0 |
| 3.15.2 | 79 | 1.051 | 0 |

[Установка в новом окружении](reproduction.txt) · [CPython 3.10.11](https://www.python.org/downloads/release/python-31011/) · [CPython 3.15.2](https://www.python.org/downloads/release/python-3152/)
