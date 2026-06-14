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
                wikistub_seed_pipeline.cmd_import(SimpleNamespace())

        output = stdout.getvalue()
        self.assertEqual(handler_events, ["load"])
        self.assertIn("JSON-Datei konnte nicht geladen werden. Abbruch.", output)

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


if __name__ == "__main__":
    unittest.main()
