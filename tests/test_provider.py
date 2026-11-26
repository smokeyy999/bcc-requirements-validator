"""Автономные тесты транспорта. Запросы и ответы моделируются в памяти."""

import io
import json
import os
from datetime import datetime, timezone
from email.message import Message
from email.utils import format_datetime
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

from requirements_validator import provider as api


def http_error(code, body, retry=None):
    headers = Message()
    if retry is not None:
        headers["Retry-After"] = retry
    return HTTPError("https://example.invalid", code, "error", headers, io.BytesIO(body.encode()))


def reply(data):
    return io.BytesIO(json.dumps(data).encode())


class ProviderTests(unittest.TestCase):
    def setUp(self):
        self.gemini = api.Gemini("fixture-secret", "fixture-model")
        pacing = patch.object(self.gemini, "_pace")
        pacing.start()
        self.addCleanup(pacing.stop)

    def test_gemini_checks_catalog_and_records_version(self):
        pages = [
            reply({"models": [], "nextPageToken": "abc"}),
            reply({"models": [{"name": "models/fixture-model", "supportedGenerationMethods": ["generateContent"]}]}),
            reply({"modelVersion": "served-001", "candidates": [
                {"finishReason": "STOP", "content": {"parts": [{"text": '{"answer":"READY"}'}]}}
            ]}),
        ]
        with patch.object(api.request, "urlopen", side_effect=pages) as send:
            self.gemini.probe()
        self.assertEqual(self.gemini.model, "served-001")
        calls = [call.args[0] for call in send.call_args_list]
        self.assertIn("pageToken=abc", calls[1].full_url)
        self.assertNotIn("fixture-secret", calls[-1].full_url)
        self.assertEqual(json.loads(calls[-1].data)["generationConfig"]["responseJsonSchema"], api.PROBE_SCHEMA)

    def test_model_must_support_generation(self):
        with patch.object(api.request, "urlopen", return_value=reply({"models": []})):
            with self.assertRaisesRegex(api.ProviderError, "каталог"):
                self.gemini.probe()

    def test_authentication_never_leaks_secret(self):
        for code, body in [(403, "fixture-secret"), (400, "API_KEY_INVALID fixture-secret")]:
            with self.subTest(code=code), patch.object(api.request, "urlopen", side_effect=http_error(code, body)) as send:
                with self.assertRaisesRegex(api.ProviderError, "доступ") as error:
                    self.gemini._request("models")
                self.assertNotIn("fixture-secret", str(error.exception))
                self.assertEqual(send.call_count, 1)

    def test_quota_is_not_retried(self):
        with patch.object(api.request, "urlopen", side_effect=http_error(429, "RequestsPerDay")) as send:
            with self.assertRaisesRegex(api.ProviderError, "квота"):
                self.gemini._request("models")
            self.assertEqual(send.call_count, 1)

    def test_rate_limit_honors_retry_after(self):
        with patch.object(api.request, "urlopen", side_effect=[http_error(429, "", "7"), reply({"ok": True})]):
            with patch.object(api.time, "sleep") as wait:
                self.assertTrue(self.gemini._request("models")["ok"])
                wait.assert_called_once_with(7)
        date = datetime(1970, 1, 1, tzinfo=timezone.utc)
        self.assertEqual(api._retry_after(format_datetime(date, usegmt=True)), 0)

    def test_google_quota_details_distinguish_zero_daily_and_short_retry(self):
        def details(*records):
            return json.dumps({"error": {"details": list(records)}})
        retry = {"@type": "type.googleapis.com/google.rpc.RetryInfo", "retryDelay": "2.25s"}
        for violation in [{"quotaId": "GenerateContentRequestsPerDayPerProjectPerModel-FreeTier"},
                          {"quotaMetric": "generate_content_free_tier_requests", "quotaValue": "0"}]:
            payload = details({"@type": "type.googleapis.com/google.rpc.QuotaFailure", "violations": [violation]}, retry)
            with patch.object(api.request, "urlopen", side_effect=http_error(429, payload)) as send:
                with self.assertRaisesRegex(api.ProviderError, "квота"):
                    self.gemini._request("models")
                self.assertEqual(send.call_count, 1)
        with patch.object(api.request, "urlopen", side_effect=[http_error(429, details(retry)), reply({})]), \
                patch.object(api.time, "sleep") as wait:
            self.gemini._request("models")
            wait.assert_called_once_with(2.25)

    def test_incomplete_answer_retries_once_with_original_schema_and_full_prompt(self):
        responses = [reply({"candidates": [{"finishReason": "MAX_TOKENS"}]}),
                     reply({"candidates": [{"finishReason": "STOP", "content": {"parts": [{"text": '{"answer":"READY"}'}]}}]})]
        with patch.object(api.request, "urlopen", side_effect=responses) as send:
            self.assertEqual(self.gemini.ask(api.PROBE_PROMPT, api.PROBE_SCHEMA), {"answer": "READY"})
            first, second = [json.loads(call.args[0].data) for call in send.call_args_list]
            self.assertEqual(first["generationConfig"], second["generationConfig"])
            self.assertTrue(second["contents"][0]["parts"][0]["text"].startswith(api.PROBE_PROMPT))

    def test_long_retry_after_exits_before_another_request(self):
        with patch.object(api.request, "urlopen", side_effect=http_error(503, "", "120")) as send:
            with self.assertRaisesRegex(api.ProviderError, "120"):
                self.gemini._request("models")
            self.assertEqual(send.call_count, 1)

    def test_timeouts_bounded(self):
        with patch.object(api.request, "urlopen", side_effect=TimeoutError), patch.object(api.time, "sleep") as wait:
            with self.assertRaisesRegex(api.ProviderError, "таймаут"):
                self.gemini._request("models")
            self.assertEqual(wait.call_count, 2)

    def test_partial_and_malformed_model_responses(self):
        for response in [
            {"candidates": [{"finishReason": "MAX_TOKENS"}]},
            {"candidates": [{"finishReason": "STOP", "content": {"parts": [{"text": "bad json"}]}}]},
            {"candidates": [{"finishReason": "STOP", "content": {"parts": [{"text": "[]"}]}}]},
            {"candidates": [{"finishReason": "STOP", "content": {"parts": [{"text": '{"a":1,"a":2}'}]}}]},
            {"candidates": []},
        ]:
            with self.subTest(response=response), patch.object(api.request, "urlopen", side_effect=lambda *a, **kw: reply(response)):
                with self.assertRaises(api.ProviderError):
                    self.gemini.ask("Вопрос", api.PROBE_SCHEMA)

    def test_dotenv_is_data_and_environment_takes_precedence(self):
        with tempfile.TemporaryDirectory() as td, patch.dict(os.environ, {"LLM_MODEL": "chosen"}, clear=True):
            path = Path(td) / ".env"
            path.write_text("# пример\nGEMINI_API_KEY='literal#value'\nLLM_MODEL=other\nX=ignored", encoding="utf-8")
            self.assertEqual(api._read_settings(path), {"LLM_MODEL": "chosen", "GEMINI_API_KEY": "literal#value"})
        with self.assertRaisesRegex(api.ProviderError, "GEMINI_API_KEY"):
            api.Gemini("", "test")

    def test_codex_timeout_and_access(self):
        with patch.object(api.shutil, "which", return_value="codex"):
            codex = api.Codex("test")
        with patch.object(api.subprocess, "run", side_effect=subprocess.TimeoutExpired("codex", 600)):
            with self.assertRaisesRegex(api.ProviderError, "таймаут"):
                codex.probe()
        for message, pattern in [(b"ERROR: 401 secret-data", "доступ"), (b"ERROR: quota exceeded", "лимит")]:
            outcome = subprocess.CompletedProcess(["codex"], 1, stderr=message)
            with patch.object(api.subprocess, "run", return_value=outcome):
                with self.assertRaisesRegex(api.ProviderError, pattern) as error:
                    codex.probe()
                self.assertNotIn("secret-data", str(error.exception))

    def test_codex_runs_in_separate_directory_with_schema(self):
        with patch.object(api.shutil, "which", return_value="codex"):
            codex = api.Codex("fixture-model")

        def respond(command, **kw):
            root = Path(kw["cwd"])
            self.assertNotEqual(root, Path.cwd())
            self.assertEqual(command[command.index("--sandbox") + 1], "read-only")
            self.assertIn("--ignore-user-config", command)
            self.assertNotIn("READY", " ".join(command))
            self.assertEqual(json.loads((root / "schema.json").read_text(encoding="utf-8")), api.PROBE_SCHEMA)
            (root / "answer.json").write_text('{"answer":"READY"}', encoding="utf-8")
            return subprocess.CompletedProcess(command, 0, stderr=b"")

        with patch.object(api.subprocess, "run", side_effect=respond):
            codex.probe()
