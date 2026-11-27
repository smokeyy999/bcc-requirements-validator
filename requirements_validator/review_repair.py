"""Apply bounded corrections to a schema-valid draft and recheck the entire result."""
from collections import Counter
from copy import deepcopy


def parse_with_repairs(draft, parse, patch, max_repairs, used=0):
    """Return only an accepted parse. Further edits require newly diagnosed paths."""
    diagnoses = []
    for attempt in range(used, max_repairs + 1):
        try:
            # A parser may normalise or annotate the object while checking it.
            # The patch always targets the exact JSON the provider saw.
            return parse(deepcopy(draft))
        except ValueError as error:
            detail = str(error)
            paths = frozenset(getattr(error, "paths", ()))
            issues = Counter(line.strip() for line in detail.splitlines() if line.strip())
            if attempt == max_repairs:
                stop = "Исчерпан лимит исправлений."
            elif attempt and (not paths or any(not isinstance(path, str) or not path.startswith("/")
                                               or len(path) < 2 for path in paths)):
                stop = "Для следующей правки не определены разрешённые поля."
            elif any(old_paths <= paths and old_issues <= issues for old_paths, old_issues in diagnoses):
                stop = "Валидация не подтвердила прогресс исправления."
            else:
                diagnoses.append((paths, issues))
                draft = patch(draft, error, attempt + 1)
                continue
            raise ValueError(f"Повторный ответ модели не прошёл проверку: {detail}. {stop} Повторите прогон.") from error
