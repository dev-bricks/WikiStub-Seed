import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import md_to_json
import wikistub_seed_cli
import wikistub_seed_pipeline
from data_policy import duplicate_locations_are_allowed
from translate import estimate_batch_max_cost_usd, estimate_max_request_cost_usd


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


class CliExitStatusTests(unittest.TestCase):
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
