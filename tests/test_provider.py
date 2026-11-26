"""Автономные проверки настройки модели и транспорта Codex CLI."""

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from requirements_validator import provider as api


class ProviderTests(unittest.TestCase):
    def test_clean_install_uses_official_model_without_config_or_api_key(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, {}, clear=True):
            path = Path(folder) / ".env"
            with patch.object(api, "Path", return_value=path), patch.object(api.shutil, "which", return_value="codex"):
                provider = api.get_provider()
        self.assertEqual((provider.model, provider.extract_workers), ("gpt-6.2-sol", 2))

    def test_environment_takes_precedence_and_only_supported_settings_are_read(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, {"LLM_MODEL": api.MODEL}, clear=True):
            path = Path(folder) / ".env"
            path.write_text("# параметры\nLLM_MODEL=old\nCODEX_EXTRACT_WORKERS='1'\nPRIVATE_KEY=test-value", encoding="utf-8")
            self.assertEqual(api._read_settings(path), {"LLM_MODEL": api.MODEL, "CODEX_EXTRACT_WORKERS": "1"})

    def test_unsupported_provider_model_or_worker_count_is_rejected_before_launch(self):
        for key, value in (("LLM_PROVIDER", "other"), ("LLM_MODEL", "other"), ("CODEX_EXTRACT_WORKERS", "3")):
            with (self.subTest(key=key), patch.object(api, "_read_settings", return_value={key: value}),
                  patch.object(api.shutil, "which") as executable):
                with self.assertRaisesRegex(api.ProviderError, key):
                    api.get_provider()
                executable.assert_not_called()

    def test_bad_json_and_duplicate_fields_are_rejected(self):
        for raw in ("not JSON", "[]", '{"result":1,"result":2}'):
            with self.subTest(raw=raw), self.assertRaises(api.ProviderError):
                api._object(raw)

    def test_codex_timeout_and_access(self):
        with patch.object(api.shutil, "which", return_value="codex"):
            codex = api.Codex()
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
            codex = api.Codex()

        def respond(command, **kw):
            root = Path(kw["cwd"])
            self.assertNotEqual(root, Path.cwd())
            self.assertEqual(command[command.index("--sandbox") + 1], "read-only")
            self.assertIn("--ignore-user-config", command)
            self.assertEqual(command[command.index("--model") + 1], "gpt-6.2-sol")
            self.assertNotIn("READY", " ".join(command))
            self.assertEqual(json.loads((root / "schema.json").read_text(encoding="utf-8")), api.PROBE_SCHEMA)
            (root / "answer.json").write_text('{"answer":"READY"}', encoding="utf-8")
            return subprocess.CompletedProcess(command, 0, stderr=b"")

        with patch.object(api.subprocess, "run", side_effect=respond):
            codex.probe()
