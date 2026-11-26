import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace

from requirements_validator.example_scope import input_scope_error, unbound_response_examples
from requirements_validator.source import read_document


def block(ident, title, text, kind="text"):
    return SimpleNamespace(id=ident, section=title, text=text, kind=kind)


class ExampleInputTests(unittest.TestCase):
    rules = "HTTP 422. Ответ, если параметры запроса недопустимы."
    section = "Сервис / Образец А / Ответ / 202. Accepted"
    response = '{"state":"deferred"}'

    def candidate(self):
        evidence = [dict(id="R-X", block="rules", quote=self.rules),
                    dict(id="R-Y", block="output", quote=self.response)]
        return dict(topic="Ответы 422 и 202 при недопустимом запросе",
                    question="Какой статус выбрать?", test="Проверить выбранный статус.",
                    counted=True, evidence=evidence, proposal_options=[dict(anchor=e) for e in evidence])

    def test_response_without_request_cannot_prove_applicability(self):
        blocks = [block("unrelated", "Сервис / Образец Б / Запрос", "POST /reserve?area=13", "code"),
                  block("output", self.section, self.response, "code")]
        unbound = unbound_response_examples(blocks)
        self.assertEqual(unbound, {"output": "202"})
        original = self.candidate()
        self.assertIn("конкретном запросе", input_scope_error(original, original, unbound))
        q = "Какой запрос воспроизводит показанный ответ для образца А?"
        good = dict(counted=False, question=q, test="Для недопустимого входа проверить 422. Отдельно повторить запрос автора.")
        self.assertEqual(input_scope_error(good, original, unbound), "")
        self.assertTrue(input_scope_error(dict(good, test="Передать один произвольный запрос."), original, unbound))
        self.assertTrue(input_scope_error(dict(good, test="Проверить выбранный статус 202 или 422."), original, unbound))
        self.assertTrue(input_scope_error(None, original, unbound))

    def test_actual_request_can_be_cited_for_a_real_conflict(self):
        for source in (
            block("request", self.section, "Запрос: lane=west"),
            block("request", "Сервис / Образец А / Запрос", '{"lane":"west"}', "code"),
            block("request", self.section, "POST /reserve?lane=west", "code"),
            block("condition", self.section, "При запросе с истёкшим пропуском вернуть HTTP 202."),
        ):
            blocks = [source, block("output", self.section, self.response, "code")]
            with self.subTest(source=source):
                unbound = unbound_response_examples(blocks)
                self.assertNotIn("output", unbound)
                self.assertEqual(input_scope_error(self.candidate(), self.candidate(), unbound), "")

    def test_alternative_response_shares_explicit_input_only_with_its_own_example(self):
        bodies = [block("request", self.section, "Запрос: ticket=x"),
                  block("before", self.section, '{"accepted":true}', "code"),
                  block("or", self.section, "или"), block("output", self.section, self.response, "code")]
        self.assertEqual(unbound_response_examples(bodies), {})
        self.assertEqual(unbound_response_examples(bodies[1:]), {"before": "202", "output": "202"})
        self.assertEqual(unbound_response_examples(bodies[:2] + bodies[3:]), {"output": "202"})

    def test_unrelated_output_does_not_change_a_schema_finding(self):
        original = self.candidate()
        original.update(topic="Тип поля в примере ответа", question="Текст или число?", test="Сверить тип поля.")
        self.assertEqual(input_scope_error(original, original, {"output": "202"}), "")

    def test_real_markdown_explicit_later_request_and_compatible_blocks(self):
        with TemporaryDirectory() as directory:
            source = Path(directory, "spec.md")
            source.write_text("# Протокол\n\n## 202. Accepted\n\n```json\n" + self.response + "\n```\n", encoding="utf8")
            blocks = read_document(source).blocks
        self.assertEqual(unbound_response_examples(blocks), {blocks[0].id: "202"})
        previous = SimpleNamespace(id="generic", text="Возможный ответ.", section=blocks[0].section)
        self.assertEqual(unbound_response_examples([previous, *blocks]), {blocks[0].id: "202"})
        following = block("linked", blocks[0].section, "Этот ответ воспроизводит запрос POST /reserve?desk=R.")
        self.assertEqual(unbound_response_examples([*blocks, following]), {})

    def test_status_heading_edit_and_an_unconditional_output_rule_are_separate(self):
        original = self.candidate()
        original.update(question="", proposal_options=[], topic="Перенести определения статусов по заголовкам")
        self.assertEqual(input_scope_error(original, original, {"output": "202"}), "")
        original = self.candidate()
        ok = dict(id="R-OK", block="success", quote="202. Ответ означает успешную постановку в очередь.")
        original["evidence"].append(ok)
        original["proposal_options"][0] = dict(anchor=ok)
        self.assertEqual(input_scope_error(original, original, {"output": "202"}), "")
