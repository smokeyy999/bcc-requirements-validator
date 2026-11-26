import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import evaluate as ev


def finding(ident, lines, category="Ясность"):
    return ev.Finding(ident, "Дефект", category, "Тестовая карточка", frozenset(lines))


def make_report(path, case, trial, rows=()):
    path.parent.mkdir(parents=True, exist_ok=True)
    text = [
        "# Отчёт автономной фикстуры",
        f"| Входной файл | [source]({case.path.resolve().as_posix()}) |",
        f"| SHA-256 исходных байтов | `{case.sha}` |",
        f"| Коммит реализации | `{'a' * 40}` |",
        "| Провайдер и модель | Тестовый · `пример` |",
        f"| Начало / окончание | 2020-01-01T10:00:{trial:02}+05:00 / 2020-01-01T10:01:00+05:00 |",
        '<a id="findings"></a>',
    ]
    for f in rows:
        text.extend([f'<a id="{f.id.lower()}"></a>', "", f"### {f.id} · {f.title}", "",
                     f"**{f.kind} · {f.category} · Существенная.** Описание."])
        for line in sorted(f.lines):
            text.extend(["", f"[R-M{line:04}-01](#id) · Раздел · [строка {line}](source.md#L{line})",
                         "", "> Доказательство."])
    text.extend(["", '<a id="decision"></a>', ""])
    path.write_text("\n".join(text), encoding="utf-8")
    return path


class BenchmarkTests(unittest.TestCase):
    def test_matrices_frozen_separate_and_all_seeds_are_actual_mutations(self):
        cases = ev.load_cases(ev.ROOT / "benchmark", "all")
        self.assertEqual(7, len(cases))
        self.assertEqual(15, sum(len(c.seeds) for c in cases))
        self.assertEqual({"dev", "test"}, {c.split for c in cases})
        self.assertEqual(4, sum(not c.seeds for c in cases))
        for case in cases:
            if not case.seeds:
                continue
            baseline = case.path.with_name("baseline.md").read_text(encoding="utf-8").splitlines()
            actual = case.path.read_text(encoding="utf-8").splitlines()
            modified = {n for n, (a, b) in enumerate(zip(baseline, actual), 1) if a != b}
            self.assertEqual(5, len(modified))
            for s in case.seeds:
                self.assertTrue(any(lo <= n <= hi for n in modified for lo, hi in s.ranges), s)

    def test_matching_requires_every_anchor_category_and_unique_pair(self):
        s = ev.Seed("S", "пример", "Ясность", ((1, 1), (3, 4)), "описание")
        pair, manual = ev.match_seeds([s], [finding("Z-1", [1, 4]), finding("Z-2", [1]),
                                           finding("Z-3", [1, 3], "Полнота")])
        self.assertEqual({"S": "Z-1"}, pair)
        self.assertEqual({"Z-2": "S", "Z-3": "S"}, manual)
        pair, manual = ev.match_seeds([s], [finding("Z-1", [1, 4]), finding("Z-2", [1, 3])])
        self.assertEqual({}, pair)
        self.assertEqual(2, len(manual))
        twin = ev.Seed("T", "пример", "Ясность", ((3, 3),), "описание")
        self.assertEqual({}, ev.match_seeds([s, twin], [finding("Z-1", [1, 3])])[0])

    def test_stability_does_not_inflate_chains_or_duplicate_findings(self):
        def report(*findings):
            return ev.Report(Path(), "", "", "", findings)
        three = [report(finding("Z-1", [2, 9])), report(finding("Z-2", [2])), report(finding("Z-3", [2]))]
        self.assertEqual([([(1, "Z-1"), (2, "Z-2"), (3, "Z-3")], False)], ev.stability(three))
        three[-1] = report(finding("Z-3", [9]))
        self.assertTrue(all(uncertain and len(group) == 1 for group, uncertain in ev.stability(three)))
        three[0] = report(finding("Z-1", [2, 9]), finding("Z-4", [2]))
        self.assertEqual(4, len(ev.stability(three)))

    def test_official_pair_checks_before_generation_and_after_relocation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "benchmark" / "ex" / "requirements.md"
            src.parent.mkdir(parents=True)
            src.write_bytes(b"Description\n")
            case = ev.Case("example", "dev", src, (), hashlib.sha256(src.read_bytes()).hexdigest(), 1)
            scratch, final = root/".tmp"/"runs", root/"reports"/"runs"
            ev.check_layout([case], scratch, final)
            with self.assertRaisesRegex(ValueError, "ссылки"):
                ev.check_layout([case], scratch/"extra", final)
            path = make_report(ev.report_path(scratch, case, 1), case, 1)
            report = ev.parse_report(path, case)
            with self.assertRaisesRegex(ValueError, "официальной"):
                ev.check_official(report, case)
            text = path.read_text(encoding="utf-8").replace('<a id="findings">',
                '| Рабочая копия при старте | чистая |\n<a id="findings">')
            path.write_text(text, encoding="utf-8")
            sidecar = path.parent / path.stem / "run-meta.json"
            sidecar.parent.mkdir()
            meta = dict(report_sha256=hashlib.sha256(path.read_bytes()).hexdigest(), source_sha256=case.sha,
                        commit=report.commit, started_at=report.started, provider="Тестовый",
                        model="пример", generation={"seed":42}, working_tree="чистая")
            sidecar.write_text(json.dumps(meta), encoding="utf-8")
            ev.check_official(ev.parse_report(path, case), case)
            sidecar.write_text(json.dumps(dict(meta, working_tree="изменена")), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "статус"):
                ev.parse_report(path, case)
            sidecar.write_text(json.dumps(dict(meta, report_sha256="e"*64)), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "другому отчёту"):
                ev.parse_report(path, case)

    def test_import_cli_is_offline_and_rejects_reused_runs_hash_or_incomplete_card(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "src.md"
            source.write_bytes(b"Example\n")
            case = ev.Case("a", "test", source, (), hashlib.sha256(source.read_bytes()).hexdigest(), 1)
            reports = [make_report(ev.report_path(root/"runs", case, i), case, i, [finding("Z-001", [1])])
                       for i in (1, 2, 3)]
            output = root / "quality.md"
            with patch.object(ev, "load_cases", return_value=[case]), patch.object(ev.subprocess, "run", side_effect=AssertionError):
                self.assertEqual(0, ev.main(["--import-dir", str(root/"runs"), "--output", str(output)]))
                self.assertIn("1/1 (100.0%)", output.read_text(encoding="utf-8"))
                self.assertIn("Вне эталонных диапазонов", output.with_name("quality-manual.md").read_text(encoding="utf-8"))
                stability = root / "stability.md"
                self.assertEqual(0, ev.main(["--stability-only", *map(str, reports), "--source", str(source),
                                             "--output", str(stability)]))
                self.assertIn("3/3", stability.read_text(encoding="utf-8"))
                result = output.read_bytes()
                reports[1].write_bytes(reports[0].read_bytes())
                self.assertEqual(1, ev.main(["--import-dir", str(root/"runs"), "--output", str(output)]))
                self.assertEqual(result, output.read_bytes())
            invalid = reports[0].read_text(encoding="utf-8").replace(case.sha, "e" * 64)
            reports[0].write_text(invalid, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                ev.parse_report(reports[0], case)
            reports[0].write_text(invalid.replace("e"*64, case.sha).replace("### Z-001", "### Z-003"), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "реестр"):
                ev.parse_report(reports[0], case)
