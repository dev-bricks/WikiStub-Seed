import unittest
import tempfile
import json
from pathlib import Path
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


if __name__ == '__main__':
    unittest.main()
