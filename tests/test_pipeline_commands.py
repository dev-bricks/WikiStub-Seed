import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "wikistub_seed_pipeline_under_test",
    PROJECT_ROOT / "wikistub_seed_pipeline.py",
)
wikistub_seed_pipeline = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(wikistub_seed_pipeline)


class PipelineCommandTests(unittest.TestCase):
    def test_cmd_export_data_writes_wrapped_exchange_file(self):
        payload_data = {
            "MetaWiki": {
                "07_Informatik_KI": {
                    "Software_Engineering": [
                        {
                            "title": "Domain-Driven Design",
                            "definition_de": "Ein Ansatz zur Modellierung komplexer Software für klare Fachdomänen.",
                            "definition_en": "A way to model complex software around business domains.",
                            "relevance": "Hilft bei der Strukturierung großer Systeme.",
                            "tags": ["Informatik", "Software Engineering"],
                        }
                    ]
                }
            }
        }

        class StaticJsonHandler:
            def __init__(self):
                self.data = payload_data

            def load(self):
                return True

        with tempfile.TemporaryDirectory() as tmp_dir:
            export_path = Path(tmp_dir) / "wikistub-seed-data-v1.json"
            stdout = io.StringIO()
            with (
                mock.patch.object(
                    wikistub_seed_pipeline,
                    "JsonHandler",
                    side_effect=lambda: StaticJsonHandler(),
                ),
                contextlib.redirect_stdout(stdout),
            ):
                exit_code = wikistub_seed_pipeline.cmd_export_data(
                    SimpleNamespace(path=str(export_path))
                )

            written = json.loads(export_path.read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 0)
        self.assertEqual(written["schema"], "wikistub-seed-data-v1")
        self.assertEqual(written["source"], "wikistub_seed.json")
        self.assertEqual(written["languages"], ["de", "en", "es", "zh", "ja", "ru"])
        self.assertEqual(written["language_model"]["required_languages"], ["de", "en"])
        self.assertEqual(written["language_model"]["canonical_fields"]["definitions"], "definitions.{lang}")
        self.assertEqual(written["stub_count"], 1)
        entry = written["data"]["MetaWiki"]["07_Informatik_KI"]["Software_Engineering"][0]
        self.assertEqual(entry["definition_de"], payload_data["MetaWiki"]["07_Informatik_KI"]["Software_Engineering"][0]["definition_de"])
        self.assertEqual(entry["definitions"]["de"], entry["definition_de"])
        self.assertEqual(entry["definitions"]["en"], entry["definition_en"])
        self.assertEqual(entry["definitions"]["es"], "")
        self.assertEqual(entry["relevance_i18n"]["de"], entry["relevance"])

    def test_wikistub_accepts_canonical_language_maps(self):
        stub = wikistub_seed_pipeline.WikiStub.from_dict(
            {
                "title": "Mehrsprachiger Stub",
                "definitions": {
                    "de": "Eine tragfähige deutsche Definition für den modernen Datenpfad.",
                    "en": "A robust English definition for the modern data path.",
                    "es": "Una definición española.",
                },
                "relevance_i18n": {
                    "de": "Hilft beim Testen der Sprachmaps.",
                    "en": "Helps test language maps.",
                },
                "tags": ["Test"],
            },
            "01_Mathematik",
            "Algebra",
        )

        serialized = stub.to_dict()

        self.assertEqual(stub.get_definition("es"), "Una definición española.")
        self.assertEqual(stub.get_definition("ja"), stub.get_definition("de"))
        self.assertEqual(serialized["definition_de"], serialized["definitions"]["de"])
        self.assertEqual(serialized["relevance"], serialized["relevance_i18n"]["de"])

    def test_import_merge_preserves_translations_and_canonical_keys(self):
        handler = wikistub_seed_pipeline.JsonHandler()
        handler.data = {
            "MetaWiki": {
                "07_Informatik_KI": {
                    "Künstliche_Intelligenz": [
                        {
                            "title": "Maschinelles Lernen",
                            "definition_de": "Alte deutsche Definition.",
                            "definition_en": "Existing English definition.",
                            "definitions": {
                                "de": "Alte deutsche Definition.",
                                "en": "Existing English definition.",
                                "es": "Definición existente.",
                            },
                            "relevance": "Alte Relevanz.",
                            "relevance_i18n": {
                                "de": "Alte Relevanz.",
                                "es": "Relevancia existente.",
                            },
                            "tags": ["KI"],
                        }
                    ]
                }
            }
        }
        imported = wikistub_seed_pipeline.WikiStub(
            title="Maschinelles Lernen",
            definition_de="Aktualisierte deutsche Definition.",
            relevance="Aktualisierte Relevanz.",
            tags=["Informatik KI", "Kuenstliche Intelligenz"],
            category="07_Informatik_KI",
            subcategory="Kuenstliche_Intelligenz",
            source_file=r"C:\\Users\\private\\Maschinelles_Lernen.md",
        )

        handler.add_stub(imported)

        self.assertNotIn("Kuenstliche_Intelligenz", handler.data["MetaWiki"]["07_Informatik_KI"])
        merged = handler.data["MetaWiki"]["07_Informatik_KI"]["Künstliche_Intelligenz"][0]
        self.assertEqual(merged["definition_de"], "Aktualisierte deutsche Definition.")
        self.assertEqual(merged["definitions"]["en"], "Existing English definition.")
        self.assertEqual(merged["definitions"]["es"], "Definición existente.")
        self.assertEqual(merged["relevance_i18n"]["es"], "Relevancia existente.")
        self.assertEqual(merged["relevance"], "Aktualisierte Relevanz.")
        self.assertEqual(merged["tags"], ["Informatik KI", "Kuenstliche Intelligenz"])
        self.assertNotIn("source_file", merged)
        self.assertNotIn("category", merged)
        self.assertNotIn("subcategory", merged)

    def test_cmd_import_aborts_when_json_load_fails(self):
        handler_events = []

        class FailingJsonHandler:
            def load(self):
                handler_events.append("load")
                return False

            def add_stub(self, stub):
                raise AssertionError("cmd_import must not add stubs after a failed load")

            def save(self):
                raise AssertionError("cmd_import must not save after a failed load")

        stub = wikistub_seed_pipeline.WikiStub(
            title="Teststub",
            definition_de="Eine ausreichend lange Testdefinition fuer den Importpfad.",
            definition_en="",
            relevance="Belegt den Repro fuer den fehlerhaften Importpfad.",
            tags=["Test"],
            category="01_Mathematik",
            subcategory="Algebra",
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            base_path = Path(tmp_dir)
            md_dir = base_path / "01_Mathematik" / "Algebra"
            md_dir.mkdir(parents=True)
            (md_dir / "test.md").write_text("# Platzhalter", encoding="utf-8")

            stdout = io.StringIO()
            with (
                mock.patch.object(
                    wikistub_seed_pipeline,
                    "JsonHandler",
                    side_effect=lambda: FailingJsonHandler(),
                ),
                mock.patch.object(wikistub_seed_pipeline, "BASE_PATH", base_path),
                mock.patch.object(wikistub_seed_pipeline, "CATEGORY_FOLDERS", ["01_Mathematik"]),
                mock.patch.object(
                    wikistub_seed_pipeline.MarkdownParser,
                    "parse_file",
                    return_value=stub,
                ),
                contextlib.redirect_stdout(stdout),
            ):
                exit_code = wikistub_seed_pipeline.cmd_import(SimpleNamespace())

        output = stdout.getvalue()
        self.assertEqual(exit_code, 1)
        self.assertEqual(handler_events, ["load"])
        self.assertIn("JSON-Datei konnte nicht geladen werden. Abbruch.", output)

    def test_cmd_validate_fails_closed_when_json_load_fails(self):
        class FailingJsonHandler:
            def load(self):
                return False

            def get_all_stubs(self):
                raise AssertionError("validation must stop after a failed load")

        stdout = io.StringIO()
        with (
            mock.patch.object(
                wikistub_seed_pipeline,
                "JsonHandler",
                side_effect=lambda: FailingJsonHandler(),
            ),
            contextlib.redirect_stdout(stdout),
        ):
            exit_code = wikistub_seed_pipeline.cmd_validate(
                SimpleNamespace(exchange=None, verbose=False)
            )

        self.assertEqual(exit_code, 1)
        self.assertIn("JSON-Datei konnte nicht geladen werden", stdout.getvalue())

    def test_cmd_validate_returns_failure_for_invalid_source_stub(self):
        invalid_stub = wikistub_seed_pipeline.WikiStub(
            title="",
            definition_de="",
            definition_en="",
            relevance="",
            tags=[],
            category="01_Mathematik",
            subcategory="Algebra",
        )

        class InvalidJsonHandler:
            data = {
                "MetaWiki": {
                    "01_Mathematik": {
                        "Algebra": [
                            {
                                "title": "Gruppe",
                                "definition_de": "Eine ausreichend lange Definition einer algebraischen Gruppe.",
                                "definition_en": "A sufficiently long definition of an algebraic group.",
                                "relevance": "Grundlage zahlreicher algebraischer Modelle.",
                                "tags": ["Mathematik"],
                            }
                        ]
                    }
                }
            }

            def load(self):
                return True

            def get_all_stubs(self):
                return [invalid_stub]

        stdout = io.StringIO()
        with (
            mock.patch.object(
                wikistub_seed_pipeline,
                "JsonHandler",
                side_effect=lambda: InvalidJsonHandler(),
            ),
            contextlib.redirect_stdout(stdout),
        ):
            exit_code = wikistub_seed_pipeline.cmd_validate(
                SimpleNamespace(exchange=None, verbose=False)
            )

        self.assertEqual(exit_code, 1)
        self.assertIn("Ungültig: 1", stdout.getvalue())

    def test_cmd_validate_accepts_valid_exchange_payload(self):
        payload = {
            "schema": "wikistub-seed-data-v1",
            "generated_at": "2026-06-01T10:11:12Z",
            "source": "wikistub_seed.json",
            "languages": ["de", "en", "es", "zh", "ja", "ru"],
            "language_model": wikistub_seed_pipeline.language_model_metadata(),
            "stub_count": 1,
            "data": {
                "MetaWiki": {
                    "01_Mathematik": {
                        "Algebra": [
                            {
                                "title": "Gruppe",
                                "definition_de": "Eine algebraische Struktur mit Verknüpfung und Inversen.",
                                "definition_en": "An algebraic structure with an operation and inverses.",
                                "relevance": "Grundlage vieler mathematischer Modelle.",
                                "tags": ["Mathematik", "Algebra"],
                            }
                        ]
                    }
                }
            },
        }

        with tempfile.TemporaryDirectory() as tmp_dir:
            payload_path = Path(tmp_dir) / "wikistub-seed-data-v1.json"
            payload_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = wikistub_seed_pipeline.cmd_validate(
                    SimpleNamespace(exchange=str(payload_path), verbose=True)
                )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn("Gültige Exporthülle", output)
        self.assertIn("Schema: wikistub-seed-data-v1", output)

    def test_cmd_validate_rejects_invalid_exchange_payload(self):
        invalid_payload = {
            "schema": "wrong-schema",
            "generated_at": "not-a-date",
            "source": "",
            "languages": ["de"],
            "stub_count": 2,
            "data": {"MetaWiki": {}},
        }

        with tempfile.TemporaryDirectory() as tmp_dir:
            payload_path = Path(tmp_dir) / "broken.json"
            payload_path.write_text(json.dumps(invalid_payload, ensure_ascii=False), encoding="utf-8")

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = wikistub_seed_pipeline.cmd_validate(
                    SimpleNamespace(exchange=str(payload_path), verbose=False)
                )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 1)
        self.assertIn("Ungültige Exporthülle", output)
        self.assertIn("schema muss 'wikistub-seed-data-v1' sein.", output)

    def test_exchange_validation_rejects_invalid_nested_shapes(self):
        base_payload = {
            "schema": "wikistub-seed-data-v1",
            "generated_at": "2026-06-01T10:11:12Z",
            "source": "wikistub_seed.json",
            "languages": ["de", "en", "es", "zh", "ja", "ru"],
            "language_model": wikistub_seed_pipeline.language_model_metadata(),
            "stub_count": 0,
            "data": {"MetaWiki": {"01_Mathematik": "not-an-object"}},
        }

        category_result = wikistub_seed_pipeline.validate_exchange_payload(base_payload)
        self.assertFalse(category_result.is_valid)
        self.assertTrue(any("01_Mathematik" in error for error in category_result.errors))

        base_payload["data"] = {
            "MetaWiki": {"01_Mathematik": {"Algebra": "not-a-list"}}
        }
        subcategory_result = wikistub_seed_pipeline.validate_exchange_payload(base_payload)
        self.assertFalse(subcategory_result.is_valid)
        self.assertTrue(any("Algebra" in error for error in subcategory_result.errors))

    def test_exchange_validation_rejects_ambiguous_metadata(self):
        payload = {
            "schema": "wikistub-seed-data-v1",
            "generated_at": "2026-06-01T10:11:12",
            "source": "wikistub_seed.json",
            "languages": ["de", "en", "es", "zh", "ja", "ru", "ru"],
            "language_model": wikistub_seed_pipeline.language_model_metadata(),
            "stub_count": False,
            "data": {"MetaWiki": {}},
        }

        result = wikistub_seed_pipeline.validate_exchange_payload(payload)

        self.assertFalse(result.is_valid)
        self.assertTrue(any("Zeitzone" in error for error in result.errors))
        self.assertTrue(any("Duplikate" in error for error in result.errors))
        self.assertTrue(any("stub_count" in error for error in result.errors))

    def test_json_handler_missing_and_corrupt_master_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "wikistub_seed.json"
            handler = wikistub_seed_pipeline.JsonHandler(path)
            self.assertFalse(handler.load())

            path.write_text("{broken", encoding="utf-8")
            self.assertFalse(handler.load())

    def test_json_handler_refuses_invalid_structure_on_save(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "wikistub_seed.json"
            handler = wikistub_seed_pipeline.JsonHandler(path)
            handler.data = {"MetaWiki": {"01_Mathematik": "broken"}}

            self.assertFalse(handler.save(create_backup=False))
            self.assertFalse(path.exists())

    def test_import_discards_all_changes_when_any_markdown_fails(self):
        valid_stub = wikistub_seed_pipeline.WikiStub(
            title="Gruppe",
            definition_de="Eine ausreichend lange algebraische Definition.",
            relevance="Grundlage zahlreicher algebraischer Modelle.",
            tags=["Mathematik"],
            category="01_Mathematik",
            subcategory="Algebra",
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            base = Path(tmp_dir)
            folder = base / "01_Mathematik" / "Algebra"
            folder.mkdir(parents=True)
            good = folder / "good.md"
            bad = folder / "bad.md"
            good.write_text("good", encoding="utf-8")
            bad.write_text("bad", encoding="utf-8")
            data_path = base / "wikistub_seed.json"
            data_path.write_text('{"MetaWiki": {}}', encoding="utf-8")

            def parse(path):
                return valid_stub if path.name == "good.md" else None

            with (
                mock.patch.object(wikistub_seed_pipeline, "BASE_PATH", base),
                mock.patch.object(wikistub_seed_pipeline, "JSON_PATH", data_path),
                mock.patch.object(
                    wikistub_seed_pipeline,
                    "CATEGORY_FOLDERS",
                    ["01_Mathematik"],
                ),
                mock.patch.object(
                    wikistub_seed_pipeline.MarkdownParser,
                    "parse_file",
                    side_effect=parse,
                ),
            ):
                exit_code = wikistub_seed_pipeline.cmd_import(
                    SimpleNamespace(allow_partial=False)
                )

            written = json.loads(data_path.read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 1)
        self.assertEqual(written, {"MetaWiki": {}})

    def test_translate_selects_empty_target_slot_without_fallback(self):
        entry = {
            "title": "Gruppe",
            "definition_de": "Eine ausreichend lange algebraische Definition.",
            "definition_en": "A sufficiently long algebraic definition.",
            "definitions": {
                "de": "Eine ausreichend lange algebraische Definition.",
                "en": "A sufficiently long algebraic definition.",
                "es": "",
            },
            "relevance": "Grundlage algebraischer Modelle.",
            "tags": ["Mathematik"],
        }
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            data_path = root / "wikistub_seed.json"
            backup_path = root / "backups"
            data_path.write_text(
                json.dumps(
                    {"MetaWiki": {"01_Mathematik": {"Algebra": [entry]}}},
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            with (
                mock.patch.object(wikistub_seed_pipeline, "JSON_PATH", data_path),
                mock.patch.object(wikistub_seed_pipeline, "BACKUP_PATH", backup_path),
                mock.patch("translate.is_available", return_value=True),
                mock.patch(
                    "translate.translate_text",
                    return_value="Una definición algebraica suficientemente larga.",
                ) as translate_text,
            ):
                exit_code = wikistub_seed_pipeline.cmd_translate(
                    SimpleNamespace(
                        limit=1,
                        confirm_api_cost=True,
                        max_budget_usd=1.0,
                        lang="es",
                        delay=0.0,
                    )
                )

            written = json.loads(data_path.read_text(encoding="utf-8"))

        translated = written["MetaWiki"]["01_Mathematik"]["Algebra"][0]
        self.assertEqual(exit_code, 0)
        translate_text.assert_called_once()
        self.assertEqual(
            translated["definitions"]["es"],
            "Una definición algebraica suficientemente larga.",
        )

    def test_translate_can_repair_missing_required_english_slot(self):
        entry = {
            "title": "Gruppe",
            "definition_de": "Eine ausreichend lange algebraische Definition.",
            "definition_en": "",
            "definitions": {
                "de": "Eine ausreichend lange algebraische Definition.",
                "en": "",
            },
            "relevance": "Grundlage algebraischer Modelle.",
            "tags": ["Mathematik"],
        }
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            data_path = root / "wikistub_seed.json"
            data_path.write_text(
                json.dumps(
                    {"MetaWiki": {"01_Mathematik": {"Algebra": [entry]}}},
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            with (
                mock.patch.object(wikistub_seed_pipeline, "JSON_PATH", data_path),
                mock.patch.object(
                    wikistub_seed_pipeline,
                    "BACKUP_PATH",
                    root / "backups",
                ),
                mock.patch("translate.is_available", return_value=True),
                mock.patch(
                    "translate.translate_text",
                    return_value="A sufficiently long algebraic definition.",
                ),
            ):
                exit_code = wikistub_seed_pipeline.cmd_translate(
                    SimpleNamespace(
                        limit=1,
                        confirm_api_cost=True,
                        max_budget_usd=1.0,
                        lang="en",
                        delay=0.0,
                    )
                )

            written = json.loads(data_path.read_text(encoding="utf-8"))

        translated = written["MetaWiki"]["01_Mathematik"]["Algebra"][0]
        self.assertEqual(exit_code, 0)
        self.assertEqual(
            translated["definitions"]["en"],
            "A sufficiently long algebraic definition.",
        )


if __name__ == "__main__":
    unittest.main()
