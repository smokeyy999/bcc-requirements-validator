import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from requirements_validator import __main__ as cli


class FileSafetyTest(unittest.TestCase):
    def test_previous_report_survives_provider_and_validation_errors(self):
        fixture = Path(__file__).parent / "fixtures" / "locker.md"
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "report.md"
            output.write_bytes(b"previous complete report")
            provider = Mock(name="fixture provider")
            with patch.object(cli, "get_provider", return_value=provider):
                for phase in ("probe", "review"):
                    with self.subTest(phase=phase):
                        provider.probe.side_effect = ValueError("ошибка доступа") if phase == "probe" else None
                        with patch.object(cli, "review", side_effect=ValueError("неполный ответ")):
                            with self.assertRaises(ValueError):
                                cli.run(fixture, output, lambda _: None)
                        self.assertEqual(output.read_bytes(), b"previous complete report")

    def test_reject_input_as_output_and_wrong_output_suffix(self):
        fixture = Path(__file__).parent / "fixtures" / "locker.md"
        with self.assertRaisesRegex(ValueError, "совпадают"):
            cli.run(fixture, fixture)
        with self.assertRaisesRegex(ValueError, ".md"):
            cli.run(fixture, Path("report.pdf"))

    def test_failure_in_replace_preserves_output_and_cleans_temp(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "existing.md"
            target.write_bytes(b"complete")
            with patch.object(cli.os, "replace", side_effect=PermissionError):
                with self.assertRaises(PermissionError):
                    cli.save_complete(target, "next")
            self.assertEqual(target.read_bytes(), b"complete")
            self.assertEqual(list(target.parent.iterdir()), [target])
