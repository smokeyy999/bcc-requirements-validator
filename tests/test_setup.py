import os
from pathlib import Path
import tempfile
import unittest

from scripts.setup_gemini import configure


class SetupTest(unittest.TestCase):
    def test_update_replaces_only_provider_settings_and_preserves_other_options(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / '.env'
            path.write_text('# local config\nLLM_PROVIDER=codex\nGEMINI_REQUESTS_PER_MINUTE=4\nGEMINI_API_KEY=old\n', encoding='utf-8')
            configure(path, 'local-test-value')
            configure(path, 'locally-replaced-test-value')
            rows = path.read_text(encoding='utf-8').splitlines()
            self.assertEqual(rows, ['# local config', 'GEMINI_REQUESTS_PER_MINUTE=4', 'LLM_PROVIDER=gemini',
                                    'LLM_MODEL=gemini-3.5-flash-lite', 'GEMINI_API_KEY=locally-replaced-test-value'])
            if os.name == 'posix':
                self.assertEqual(path.stat().st_mode & 0o077, 0)
            with self.assertRaises(ValueError):
                configure(path, 'more\nthan one line')
            self.assertEqual(rows, path.read_text(encoding='utf-8').splitlines())
