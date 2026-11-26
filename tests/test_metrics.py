import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from requirements_validator import __main__ as cli
from requirements_validator import engine
from requirements_validator import provider as api
from requirements_validator.metrics import RunMetrics, purpose, stage, transport


class RunMeasurementsTest(unittest.TestCase):
    def test_codex_usage_is_captured_from_turn_event_only(self):
        def respond(command, **kwargs):
            self.assertIn("--json", command)
            Path(command[command.index("--output-last-message") + 1]).write_bytes(b"{}")
            events = [
                {"type": "item.completed", "text": "private result", "usage": {"input_tokens": 999}},
                {"type": "turn.completed", "usage": {"input_tokens": 20, "output_tokens": 7, "cached_input_tokens": 13}},
            ]
            stdout = "\n".join(json.dumps(e) for e in events).encode()
            return subprocess.CompletedProcess(command, 0, stdout, b"")

        run = RunMetrics()
        with patch.object(api.shutil, "which", return_value="codex"), run.capture(), \
                patch.object(api.subprocess, "run", side_effect=respond):
            api.Codex().ask("private result", api.PROBE_SCHEMA)
        summary = run.summary()
        self.assertEqual(summary["tokens"], {"input_tokens": 20, "output_tokens": 7,
                                             "cached_input_tokens": 13, "reasoning_tokens": None})
        self.assertIsNone(summary["cost_usd"])
        self.assertNotIn("private result", json.dumps(summary))

    def test_catalog_does_not_count_as_generation_and_unknown_usage_is_null(self):
        run = RunMetrics()
        with run.capture():
            stage("probe")
            with transport("catalog"):
                pass
            with transport("generation"):
                pass
        data = run.summary()
        self.assertEqual((data["model_calls"], data["transport_requests"], data["calls_without_io_tokens"]), (1, 2, 1))
        self.assertIsNone(data["tokens"]["output_tokens"])

    def test_second_file_failure_preserves_previous_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "one.md"
            sidecar = report.with_suffix("") / "run-meta.json"
            original = cli.save_complete
            def write(path, content):
                if path == report:
                    raise PermissionError("report in use")
                return original(path, content)
            def meta(content):
                return {"report_sha256": hashlib.sha256(content.encode()).hexdigest()}
            cli.publish(report, "before", sidecar, meta("before"))
            previous = sidecar.read_bytes()
            with patch.object(cli, "save_complete", side_effect=write), self.assertRaises(PermissionError):
                cli.publish(report, "after", sidecar, meta("after"))
            self.assertEqual(report.read_text(), "before")
            self.assertEqual(sidecar.read_bytes(), previous)
            self.assertFalse((sidecar.parent / ".pending.json").exists())

    def test_sidecar_belongs_to_exact_saved_report_even_with_two_output_names(self):
        from unittest.mock import Mock
        fixture = Path(__file__).parent / "fixtures" / "locker.md"
        provider = Mock()
        provider.name = provider.model = "fixture"
        provider.configuration.return_value = {"requested_model": "fixture"}
        result = {"counts": {"requirements": 0, "defects": 0, "questions": 0}, "findings": [], "questions": []}
        with tempfile.TemporaryDirectory() as folder, patch.object(cli, "get_provider", return_value=provider), \
                patch.object(cli, "review", return_value=result), patch.object(cli, "render", return_value="Проверка\n"):
            for stem in ("first", "second"):
                report = Path(folder) / f"{stem}.md"
                cli.run(fixture, report, lambda message: None)
                data = json.loads((Path(folder) / stem / "run-meta.json").read_bytes())
                self.assertEqual(data["report"], report.name)
                self.assertEqual(data["report_sha256"], hashlib.sha256(report.read_bytes()).hexdigest())
                self.assertEqual(data["source_sha256"], hashlib.sha256(fixture.read_bytes()).hexdigest())

    def test_parallel_extraction_keeps_context_order_and_request_accounting(self):
        from threading import Barrier
        ready = Barrier(2, timeout=4)
        a, b = (SimpleNamespace(id=ident, section="Контекст", text="Обзор.") for ident in ("A", "B"))
        document = SimpleNamespace(blocks=[a, b])
        def local(provider, batch, blocks, progress):
            with purpose("block_retry" if batch == [a] else "initial"), transport("generation"):
                ready.wait()
            return [], [batch[0].id]
        run = RunMetrics()
        with run.capture(), patch.object(engine, "_batches", return_value=[[a], [b]]), \
                patch.object(engine, "_local_review", side_effect=local), \
                patch.object(engine, "_trace_scope", return_value=({}, {})), \
                patch.object(engine, "_source", return_value={}), \
                patch.object(engine, "_request", side_effect=[([], {}, {}), ([], {}, {})]):
            result = engine.review(document, SimpleNamespace(extract_workers=2))
        self.assertEqual(result["context"], ["A", "B"])
        summary = run.summary()
        self.assertEqual(summary["model_calls"], 2)
        self.assertEqual(summary["repair_model_calls"], 1)
        self.assertEqual([r["stage"] for r in summary["requests"]], ["extract", "extract"])
