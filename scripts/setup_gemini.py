"""Set up the local Gemini API key from an interactive terminal."""
import getpass
import os
from pathlib import Path
import sys
import tempfile


def configure(path, key):
    key = key.strip()
    if not key or any(c.isspace() for c in key) or key.startswith(('http:', 'https:')):
        raise ValueError('Вставьте ключ целиком из Google AI Studio.')
    existing = path.read_text(encoding='utf-8-sig').splitlines() if path.exists() else []
    settings = dict(LLM_PROVIDER='gemini', LLM_MODEL='gemini-3.5-flash-lite', GEMINI_API_KEY=key)
    lines = [s for s in existing if s.partition('=')[0].strip() not in settings]
    lines.extend(f'{name}={value}' for name, value in settings.items())
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', newline='\n', dir=path.parent,
                                         prefix='.env.', suffix='.tmp', delete=False) as out:
            tmp = Path(out.name)
            out.write('\n'.join(lines) + '\n')
            out.flush()
            os.fsync(out.fileno())
        os.replace(tmp, path)
    finally:
        if tmp:
            tmp.unlink(missing_ok=True)


def main():
    if not sys.stdin.isatty() or not sys.stderr.isatty():
        print('Откройте обычный интерактивный терминал для скрытого ввода ключа.', file=sys.stderr)
        return 1
    print('Откройте https://aistudio.google.com/apikey и скопируйте свой ключ.')
    try:
        key = getpass.getpass('Вставьте ключ Gemini и нажмите Enter (символы скрыты): ')
        configure(Path(__file__).resolve().parents[1] / '.env', key)
    except (EOFError, KeyboardInterrupt):
        return 1
    except (OSError, ValueError) as exc:
        print(f'Не удалось записать настройки: {exc}', file=sys.stderr)
        return 1
    print('Доступ настроен в локальном .env. Ключ будет проверен при запуске агента.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
