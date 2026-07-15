import unittest
import tempfile
from pathlib import Path
from language_model import SUPPORTED_LANGUAGES
from translator import TranslationSystem


class TestTranslationSystem(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.app_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_is_german_with_german_words(self):
        ts = TranslationSystem(default_lang='de', app_dir=self.app_dir)
        # Should detect German hints
        self.assertTrue(ts._is_german("datei"))
        self.assertTrue(ts._is_german("ok")) # 'o' in hints? Wait, 'ok' contains 'o', let's check hints: 'ok' is in hints!
        self.assertTrue(ts._is_german("speichern"))

    def test_is_german_with_umlauts(self):
        ts = TranslationSystem(default_lang='de', app_dir=self.app_dir)
        self.assertTrue(ts._is_german("Gefäße"))
        self.assertTrue(ts._is_german("Groß"))

    def test_is_german_should_not_match_plain_english(self):
        ts = TranslationSystem(default_lang='de', app_dir=self.app_dir)
        # Plain English words without hints or umlauts/transliterations should NOT be German
        # e.g., "the", "value", "open", "file"
        # In the buggy implementation, "the" contains 'e' which is in "aeoeueAeOeUess", so it returns True.
        # It should return False.
        self.assertFalse(ts._is_german("the"))
        self.assertFalse(ts._is_german("value"))
        self.assertFalse(ts._is_german("open"))
        self.assertFalse(ts._is_german("file"))

    def test_corrupt_translation_file_is_not_silently_overwritten(self):
        locales = self.app_dir / "locales"
        locales.mkdir()
        translations = locales / "translations.json"
        translations.write_text("{broken", encoding="utf-8")

        with self.assertRaises(RuntimeError):
            TranslationSystem(default_lang="de", app_dir=self.app_dir)

        self.assertEqual(translations.read_text(encoding="utf-8"), "{broken")

    def test_new_keys_have_all_supported_language_slots(self):
        ts = TranslationSystem(default_lang="de", app_dir=self.app_dir)
        self.assertEqual(ts.t("Datei speichern"), "Datei speichern")
        self.assertEqual(
            list(ts.translations["Datei speichern"]),
            SUPPORTED_LANGUAGES,
        )


if __name__ == '__main__':
    unittest.main()
