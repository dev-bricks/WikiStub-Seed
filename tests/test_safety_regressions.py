import json
import math
import contextlib
import io
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import md_to_json
import check_duplicates
import wikistub_seed_cli
import wikistub_seed_pipeline
from data_policy import duplicate_locations_are_allowed
from translate import (
    estimate_batch_max_cost_usd,
    estimate_max_request_cost_usd,
    translate_batch,
)


class UnicodeImportSafetyTests(unittest.TestCase):
    def test_markdown_cleaners_preserve_unicode_content(self):
        text = "Quantenmaß μ – 同期"

        self.assertEqual(md_to_json.clean_text(text), text)
        self.assertEqual(wikistub_seed_pipeline.MarkdownParser._clean_text(text), text)

    def test_md_to_json_merge_preserves_existing_language_maps(self):
        data = {
            "MetaWiki": {
                "11_Geschichte_Archäologie": {
                    "Ur_Frühgeschichte": [
                        {
                            "title": "Bronzezeit",
                            "definition_de": "Alt.",
                            "definition_en": "Bronze Age.",
                            "definitions": {"de": "Alt.", "en": "Bronze Age.", "ja": "青銅器時代"},
                            "relevance": "Alt.",
                            "relevance_i18n": {"de": "Alt.", "ja": "重要です。"},
                            "tags": ["Geschichte"],
                        }
                    ]
                }
            }
        }
        incoming = {
            "title": "Bronzezeit",
            "definition_de": "Neu.",
            "definition_en": "",
            "definitions": {"de": "Neu.", "en": "", "ja": ""},
            "relevance": "Neue Relevanz.",
            "relevance_i18n": {"de": "Neue Relevanz.", "ja": ""},
            "tags": ["Geschichte Archaeologie", "Ur Fruehgeschichte"],
            "_category": "11_Geschichte_Archaeologie",
            "_subcategory": "Ur_Fruehgeschichte",
        }

        self.assertEqual(md_to_json.add_stub_to_data(data, incoming), "updated")

        self.assertNotIn("11_Geschichte_Archaeologie", data["MetaWiki"])
        merged = data["MetaWiki"]["11_Geschichte_Archäologie"]["Ur_Frühgeschichte"][0]
        self.assertEqual(merged["definition_de"], "Neu.")
        self.assertEqual(merged["definitions"]["en"], "Bronze Age.")
        self.assertEqual(merged["definitions"]["ja"], "青銅器時代")
        self.assertEqual(merged["relevance_i18n"]["ja"], "重要です。")
        self.assertEqual(merged["relevance"], "Neue Relevanz.")
        self.assertEqual(merged["tags"], ["Geschichte Archaeologie", "Ur Fruehgeschichte"])

    def test_markdown_parser_preserves_explicit_english_and_tags(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = (
                Path(tmp_dir)
                / "01_Mathematik"
                / "Algebra"
                / "Gruppe.md"
            )
            path.parent.mkdir(parents=True)
            path.write_text(
                "# Gruppe\n\n"
                "**Definition (DE):**\nEine algebraische Struktur.\n\n"
                "**Definition (EN):**\nAn algebraic structure.\n\n"
                "**Relevanz:**\nGrundlage der Algebra.\n\n"
                "**Tags:**\nMathematik, Algebra\n",
                encoding="utf-8",
            )

            stub = md_to_json.parse_md_file(path)

        self.assertEqual(stub["definitions"]["en"], "An algebraic structure.")
        self.assertEqual(stub["tags"], ["Mathematik", "Algebra"])

    def test_non_german_markdown_export_roundtrips_language_and_relevance(self):
        stub = wikistub_seed_pipeline.WikiStub(
            title="Gruppe",
            definition_de="Eine algebraische Struktur mit neutralem Element.",
            definition_en="An algebraic structure with an identity element.",
            definitions={"es": "Una estructura algebraica con elemento neutro."},
            relevance="Grundlage der Algebra.",
            relevance_i18n={"es": "Fundamento del álgebra."},
            tags=["Mathematik", "Algebra"],
            category="01_Mathematik",
            subcategory="Algebra",
        )
        content = wikistub_seed_pipeline.MarkdownGenerator.generate(
            stub,
            language="es",
        )
        source = str(Path("01_Mathematik") / "Algebra" / "Gruppe.md")

        pipeline_stub = wikistub_seed_pipeline.MarkdownParser.parse_content(
            content,
            source,
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / source
            path.parent.mkdir(parents=True)
            path.write_text(content, encoding="utf-8")
            legacy_stub = md_to_json.parse_md_file(path)

        self.assertEqual(pipeline_stub.definitions["es"], stub.definitions["es"])
        self.assertEqual(
            pipeline_stub.relevance_i18n["es"],
            stub.relevance_i18n["es"],
        )
        self.assertEqual(pipeline_stub.definitions["de"], stub.definitions["de"])
        self.assertEqual(legacy_stub["definitions"]["es"], stub.definitions["es"])
        self.assertEqual(
            legacy_stub["relevance_i18n"]["es"],
            stub.relevance_i18n["es"],
        )


class CliExitStatusTests(unittest.TestCase):
    def test_add_requires_english_definition_and_relevance(self):
        stderr = io.StringIO()
        with (
            contextlib.redirect_stderr(stderr),
            self.assertRaises(SystemExit) as raised,
        ):
            wikistub_seed_cli.main([
                "add",
                "--title", "Gruppe",
                "--definition", "Eine algebraische Struktur.",
                "--category", "01_Mathematik",
                "--subcategory", "Algebra",
            ])

        self.assertEqual(raised.exception.code, 2)
        self.assertIn("--definition-en", stderr.getvalue())
        self.assertIn("--relevance", stderr.getvalue())

    def test_check_propagates_child_failure(self):
        args = SimpleNamespace(similar=False)
        failed = subprocess.CompletedProcess([], 7)

        with mock.patch("subprocess.run", return_value=failed):
            self.assertEqual(wikistub_seed_cli.cmd_check(args), 7)

    def test_import_propagates_child_failure(self):
        args = SimpleNamespace(dry_run=False)
        failed = subprocess.CompletedProcess([], 9)

        with mock.patch("subprocess.run", return_value=failed):
            self.assertEqual(wikistub_seed_cli.cmd_import_md(args), 9)

    def test_translation_requires_explicit_call_limit_and_cost_confirmation(self):
        self.assertEqual(
            wikistub_seed_pipeline.cmd_translate(
                SimpleNamespace(limit=None, confirm_api_cost=False)
            ),
            1,
        )
        self.assertEqual(
            wikistub_seed_pipeline.cmd_translate(
                SimpleNamespace(limit=2, confirm_api_cost=False)
            ),
            1,
        )

    def test_translation_requires_explicit_dollar_budget(self):
        self.assertEqual(
            wikistub_seed_pipeline.cmd_translate(
                SimpleNamespace(
                    limit=2,
                    confirm_api_cost=True,
                    max_budget_usd=None,
                )
            ),
            1,
        )

    def test_translation_cost_ceiling_is_positive_and_additive(self):
        one = estimate_max_request_cost_usd("Eine kurze Definition.")
        batch = estimate_batch_max_cost_usd(
            ["Eine kurze Definition.", "Eine zweite Definition."]
        )

        self.assertGreater(one, 0)
        self.assertGreater(batch, one)

    def test_translation_batch_rejects_non_finite_limits(self):
        with self.assertRaises(ValueError):
            translate_batch(["Text"], max_budget_usd=math.nan)
        with self.assertRaises(ValueError):
            translate_batch(["Text"], delay=math.inf, max_budget_usd=1)

    def test_translation_batch_sleeps_only_after_success(self):
        with (
            mock.patch("translate.translate_text", side_effect=["", "ok", "done"]),
            mock.patch("translate.time.sleep") as sleep,
        ):
            result = translate_batch(
                ["eins", "zwei", "drei"],
                delay=0.5,
                max_budget_usd=1,
            )

        self.assertEqual(result, ["", "ok", "done"])
        sleep.assert_called_once_with(0.5)


class DuplicatePolicyTests(unittest.TestCase):
    def test_only_reviewed_cross_domain_duplicate_locations_are_allowed(self):
        self.assertTrue(
            duplicate_locations_are_allowed(
                "Graphentheorie",
                [
                    ("07_Informatik_KI", "Theoretische_Informatik"),
                    ("01_Mathematik", "Diskrete_Mathematik"),
                ],
            )
        )
        self.assertFalse(
            duplicate_locations_are_allowed(
                "Graphentheorie",
                [
                    ("07_Informatik_KI", "Theoretische_Informatik"),
                    ("01_Mathematik", "Analysis"),
                ],
            )
        )

    def test_interactive_fix_removes_identifier_equivalent_titles(self):
        data = {
            "MetaWiki": {
                "A": {"One": [{"title": "Foo-Bar"}]},
                "B": {"Two": [{"title": "foo bar"}]},
            }
        }
        stubs = check_duplicates.get_all_stubs(data)
        duplicates = check_duplicates.find_exact_duplicates(stubs)

        with mock.patch("builtins.input", return_value="1"):
            removed = check_duplicates.fix_duplicates_interactive(data, duplicates)

        remaining = sum(
            len(entries)
            for subcategories in data["MetaWiki"].values()
            for entries in subcategories.values()
        )
        self.assertEqual(removed, 1)
        self.assertEqual(remaining, 1)


class SafeIoTests(unittest.TestCase):
    def test_safe_path_component_blocks_traversal_and_windows_reserved_names(self):
        from safe_io import safe_path_component

        for raw in ("../outside", r"..\outside", "CON", "a:b", "title?.md"):
            component = safe_path_component(raw)
            self.assertNotIn("/", component)
            self.assertNotIn("\\", component)
            self.assertNotIn(":", component)
            self.assertNotIn("?", component)
            self.assertNotIn(component.upper().split(".")[0], {"CON", "PRN", "AUX", "NUL"})
            self.assertNotIn(component, {"", ".", ".."})

    def test_atomic_json_write_keeps_original_when_replace_fails(self):
        from safe_io import atomic_write_json

        with tempfile.TemporaryDirectory() as tmp_dir:
            target = Path(tmp_dir) / "data.json"
            target.write_text('{"state": "old"}', encoding="utf-8")

            with mock.patch("safe_io.os.replace", side_effect=OSError("disk failure")):
                with self.assertRaises(OSError):
                    atomic_write_json(target, {"state": "new"})

            self.assertEqual(json.loads(target.read_text(encoding="utf-8")), {"state": "old"})

    def test_atomic_json_rejects_non_standard_nan(self):
        from safe_io import atomic_write_json

        with tempfile.TemporaryDirectory() as tmp_dir:
            target = Path(tmp_dir) / "data.json"
            with self.assertRaises(ValueError):
                atomic_write_json(target, {"budget": math.nan})
            self.assertFalse(target.exists())

    def test_backup_retention_rejects_zero(self):
        from safe_io import backup_file

        with tempfile.TemporaryDirectory() as tmp_dir:
            source = Path(tmp_dir) / "data.json"
            source.write_text("{}", encoding="utf-8")
            with self.assertRaises(ValueError):
                backup_file(source, Path(tmp_dir) / "backup", prefix="data", keep=0)

    def test_safe_path_component_honors_exact_maximum(self):
        from safe_io import safe_path_component

        component = safe_path_component("a/very/long/unsafe/title", max_length=20)
        self.assertLessEqual(len(component), 20)

    def test_markdown_export_confines_untrusted_path_components(self):
        from safe_io import safe_path_component

        stub = wikistub_seed_pipeline.WikiStub(
            title=r"..\outside:stub?",
            definition_de="Eine ausreichend lange Definition mit sicherem Exportziel.",
            relevance="Belegt die Pfadbegrenzung.",
            category="01_Mathematik",
            subcategory=r"..\escape",
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            output = Path(tmp_dir) / "output"
            self.assertTrue(
                wikistub_seed_pipeline.MarkdownGenerator.write_file(stub, output)
            )
            expected = (
                output
                / safe_path_component(stub.category)
                / safe_path_component(stub.subcategory)
                / f"{safe_path_component(stub.title)}.md"
            )
            self.assertTrue(expected.is_file())
            self.assertTrue(expected.resolve().is_relative_to(output.resolve()))


if __name__ == "__main__":
    unittest.main()
