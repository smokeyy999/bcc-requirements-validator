import json
from pathlib import Path
from types import SimpleNamespace
import unittest

from requirements_validator.response_matrix import response_matrix
from requirements_validator.source import read_document


ROOT = Path(__file__).resolve().parents[1]


def block(identifier, kind, section, text):
    return SimpleNamespace(id=identifier, kind=kind, section=section, text=text)


class ResponseMatrixTests(unittest.TestCase):
    def test_full_document_coverage_accepts_an_ordered_mapping_view_and_a_single_pass_iterator(self):
        blocks = read_document(ROOT / "docs/requirements.md").blocks
        expected = response_matrix(blocks)
        self.assertTrue(expected["contracts"][0]["examples"])
        indexed = {block.id: block for block in blocks}
        self.assertEqual(response_matrix(indexed.values()), expected)
        self.assertEqual(response_matrix(iter(blocks)), expected)

    def test_three_real_inputs_preserve_conditions_and_all_source_branches(self):
        for path in ("docs/requirements.md", "checks/pdf/requirements-copy.pdf", "checks/docx/requirements-copy.docx"):
            with self.subTest(path=path):
                document = read_document(ROOT / path)
                source_ids = {b.id for b in document.blocks}
                matrix = response_matrix(document.blocks)
                self.assertEqual(json.loads(json.dumps(matrix)), matrix)
                contract, = matrix["contracts"]
                fields = contract["fields"]
                self.assertEqual([f["name"] for f in fields], ["result", "amount", "enabled", "message"])
                self.assertEqual([f["type"] for f in fields], ["string"] * 4)
                self.assertEqual(fields[1]["conditions"]["Logic"], "При успехе")
                self.assertEqual(fields[3]["conditions"]["Logic"], "При ошибке")
                examples = contract["examples"]
                self.assertEqual([e["heading_status"] for e in examples], ["200", "200", "400", "401", "403", "500"])
                self.assertEqual([e["keys"] for e in examples],
                                 [["result", "amount", "enabled"], ["result", "message"]] + [["message"]] * 4)
                self.assertEqual(examples[-2]["inline_status"], "404")
                self.assertIn(examples[-2]["label_block"], source_ids)
                self.assertTrue(all(row["block"] in source_ids for row in fields + examples))

    def test_endpoints_requests_and_objects_remain_scoped(self):
        headers = " / Столбцы: Type · Field name · Required · Description"
        first = "Service / Count"
        second = "Service / Scan"
        blocks = [
            block("a", "table", first + " / Response" + headers, "| integer | count | optional | Count |"),
            block("b", "table", first + " / Request" + headers, "| uuid | token | yes | Credential |"),
            block("c", "code", first + " / Request / Statuses / 202", '{"token":"example"}'),
            block("d", "code", first + " / Statuses / 202", '{}'),
            block("e", "table", second + " / Response" + headers, "object\trow\twhen found\tRecord"),
            block("f", "code", second + " / Response / Found", '{"row":{"nested":1},"tail":false}'),
            block("g", "code", second + " / Response / Retry", '["bad root"]'),
            block("h", "code", second + " / Response / Lost", '{bad json}'),
        ]
        first_contract, second_contract = response_matrix(blocks)["contracts"]
        self.assertEqual(first_contract["fields"], [dict(block="a", name="count", type="integer",
                                                         conditions={"Required": "optional"}, description="Count")])
        self.assertEqual(first_contract["examples"], [dict(block="d", branch="202", keys=[], heading_status="202")])
        self.assertEqual(second_contract["fields"][0]["name"], "row")
        self.assertEqual(second_contract["examples"], [dict(block="f", branch="Found", keys=["row", "tail"])])

    def test_unknown_blocks_and_examples_without_declarations_are_ignored(self):
        blocks = [
            SimpleNamespace(text="no parser metadata"),
            block("a", "table", "Столбцы: Name · Type", "x\tint"),
            block("b", "table", "API / Request / Столбцы: Name · Type", "x\tint"),
            block("c", "code", "API / Status codes / 201", '{"x":0}'),
        ]
        self.assertEqual(response_matrix(blocks), {})
