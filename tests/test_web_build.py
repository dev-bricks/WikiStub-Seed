import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "wikistub_web_build_under_test",
    PROJECT_ROOT / "web_publisher" / "_build.py",
)
web_build = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(web_build)


class WebBuildSafetyTests(unittest.TestCase):
    def test_invalid_nested_source_preserves_both_existing_outputs(self):
        malformed = {
            "MetaWiki": {
                "01_Mathematik": {
                    "Algebra": ["not-an-object"],
                }
            }
        }
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            source = root / "wikistub_seed.json"
            out_dir = root / "data"
            out_dir.mkdir()
            out_data = out_dir / "wikistub_seed.json"
            out_index = out_dir / "search-index.json"
            source.write_text(json.dumps(malformed), encoding="utf-8")
            out_data.write_text('{"sentinel": "data"}\n', encoding="utf-8")
            out_index.write_text('[{"sentinel": "index"}]\n', encoding="utf-8")
            before_data = out_data.read_bytes()
            before_index = out_index.read_bytes()

            with (
                mock.patch.object(web_build, "SRC", source),
                mock.patch.object(web_build, "OUT_DIR", out_dir),
                mock.patch.object(web_build, "OUT_DATA", out_data),
                mock.patch.object(web_build, "OUT_INDEX", out_index),
            ):
                with self.assertRaises(ValueError):
                    web_build.build()

            self.assertEqual(out_data.read_bytes(), before_data)
            self.assertEqual(out_index.read_bytes(), before_index)


if __name__ == "__main__":
    unittest.main()
