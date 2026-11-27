import json
import unittest

from requirements_validator.engine import PATCH, STR, DraftError, _request, obj
from requirements_validator.metrics import RunMetrics, transport


SCHEMA = obj(first=STR, second=STR, third=STR, fourth=STR, note=STR)
DRAFT = dict(first="", second="", third="", fourth="да", note="оставить")


def replace(field, value="да"):
    return {"changes": [{"op": "replace", "path": "/" + field, "value": value}]}


def first_error(data):
    for field in ("first", "second", "third", "fourth"):
        if data[field] != "да":
            raise DraftError(f"Требуется значение в {field}", ["/" + field])
    return data


class Answers:
    def __init__(self, *answers):
        self.answers = iter(answers)
        self.calls = []

    def ask(self, prompt, schema):
        with transport("generation"):
            self.calls.append((prompt, schema))
            return next(self.answers)

    def run(self, parse=first_error, **options):
        return _request(self, "Проверь.", {}, SCHEMA, parse, lambda message: None, **options)


class BoundedRepairTests(unittest.TestCase):
    def test_three_patches_use_current_draft_paths_and_existing_request_accounting(self):
        provider = Answers(DRAFT, replace("first"), replace("second"), replace("third"))
        metrics = RunMetrics()
        with metrics.capture():
            result = provider.run(max_repairs=3)
        self.assertEqual(result, dict.fromkeys(("first", "second", "third", "fourth"), "да") | {"note": "оставить"})
        self.assertEqual([schema for _, schema in provider.calls], [SCHEMA, PATCH, PATCH, PATCH])
        prompts = [json.loads(prompt.rsplit("\nВход (JSON):\n", 1)[1]) for prompt, _ in provider.calls[1:]]
        self.assertEqual([p["allowed_paths"] for p in prompts], [["/first"], ["/second"], ["/third"]])
        self.assertEqual([p["draft"]["second"] for p in prompts], ["", "", "да"])
        self.assertEqual(DRAFT["first"], "")
        self.assertEqual(metrics.summary()["repair_model_calls"], 3)

    def test_previously_allowed_field_becomes_protected(self):
        provider = Answers(DRAFT, replace("first"), replace("first", "постороннее"))
        with self.assertRaisesRegex(ValueError, "Путь вне разрешённой области"):
            provider.run(max_repairs=3)
        self.assertEqual(len(provider.calls), 3)

    def test_repeated_diagnosis_without_progress_stops_and_rejects(self):
        provider = Answers(DRAFT, replace("first", "нет"))
        with self.assertRaisesRegex(ValueError, "не подтвердила прогресс"):
            provider.run(max_repairs=3)
        self.assertEqual(len(provider.calls), 2)

    def test_legacy_single_repair_and_three_patch_ceiling(self):
        for options, expected in [({}, 1), ({"max_repairs": 3}, 3)]:
            with self.subTest(options=options):
                source = dict(DRAFT, fourth="")
                provider = Answers(source, replace("first"), replace("second"), replace("third"))
                with self.assertRaisesRegex(ValueError, "Исчерпан лимит"):
                    provider.run(**options)
                self.assertEqual(len(provider.calls), expected + 1)
        for limit in (0, 4, True):
            with self.subTest(limit=limit), self.assertRaisesRegex(ValueError, "max_repairs"):
                Answers().run(max_repairs=limit)

    def test_pathless_diagnosis_allows_first_patch_but_never_grants_an_unrestricted_second(self):
        def check(data):
            if not data["first"]:
                raise ValueError("Укажите начальное значение")
            if not data["second"]:
                raise ValueError("Укажите следующее значение")
            return data
        provider = Answers(DRAFT, replace("first"))
        with self.assertRaisesRegex(ValueError, "не определены разрешённые поля"):
            provider.run(check, max_repairs=3)
        self.assertEqual(len(provider.calls), 2)
        provider = Answers(dict(DRAFT, second="да"), replace("first"))
        self.assertEqual(provider.run(check, max_repairs=3)["first"], "да")

    def test_schema_retry_also_consumes_one_of_the_three_repairs(self):
        provider = Answers({}, DRAFT, replace("first"), replace("second"))
        with self.assertRaisesRegex(ValueError, "Исчерпан лимит"):
            provider.run(max_repairs=3)
        self.assertEqual([schema for _, schema in provider.calls], [SCHEMA, SCHEMA, PATCH, PATCH])

    def test_empty_path_cannot_grant_a_second_patch_access_to_every_field(self):
        def check(data):
            if not data["first"]:
                raise DraftError("Первое поле пока пустое", ["/first"])
            raise DraftError("Нет локализованного поля для продолжения", [""])
        provider = Answers(DRAFT, replace("first"))
        with self.assertRaisesRegex(ValueError, "не определены разрешённые поля"):
            provider.run(check, max_repairs=3)
        self.assertEqual(len(provider.calls), 2)
