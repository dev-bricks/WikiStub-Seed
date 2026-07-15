"""
TranslationSystem - Multi-Language Support für Anwendungen
============================================================
Version: 1.0.0 (isoliert aus _LANG)
Quelle: ARC_EntwicklungsschleifeAdvanced/TranslationSystem.py v2.4

Verwendung:
-----------
from translator import TranslationSystem

translator = TranslationSystem('de')
label.setText(translator.t('Datei oeffnen'))
translator.set_language('en')
"""

import re
from pathlib import Path
from typing import Dict, List, Set

from language_model import SUPPORTED_LANGUAGES, normalize_language_code
from safe_io import JsonDataError, atomic_write_json, read_json_object


class TranslationSystem:
    """Multi-Language Support System v1.0"""

    def __init__(self, default_lang: str = 'de', app_dir: Path = None):
        """
        Initialisiert Translation-System.

        Args:
            default_lang: Standard-Sprache ('de' oder 'en')
            app_dir: Verzeichnis der Anwendung (default: aktuelles Verzeichnis)
        """
        normalized_default = normalize_language_code(default_lang)
        if normalized_default not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language: {default_lang}")
        self.current_lang = normalized_default

        if app_dir is None:
            app_dir = Path.cwd()
        self.app_dir = Path(app_dir)

        self.translations_file = self.app_dir / "locales" / "translations.json"

        self.string_patterns = [
            re.compile(r'setText\s*\(\s*["\']([^"\']+)["\']\s*\)'),
            re.compile(r'setWindowTitle\s*\(\s*["\']([^"\']+)["\']\s*\)'),
            re.compile(r'QLabel\s*\(\s*["\']([^"\']+)["\']\s*\)'),
            re.compile(r'QPushButton\s*\(\s*["\']([^"\']+)["\']\s*\)'),
            re.compile(r'addAction\s*\([^,]*["\']([^"\']+)["\']\s*\)'),
            re.compile(r'addTab\s*\([^,]+,\s*["\']([^"\']+)["\']\s*\)'),
            re.compile(r'text\s*=\s*"([^"]+)"'),
        ]

        self.german_hints = [
            "datei", "bearbeiten", "ansicht", "hilfe", "oeffnen", "speichern",
            "schliessen", "einstellungen", "abbrechen", "ok", "ja", "nein",
            "start", "stop", "pause", "fortsetzen", "laden", "aktualisieren",
            "filter", "fehler", "export", "import", "optionen", "anzeigen",
        ]

        self.translations = {}
        self._load_translations()

    def _load_translations(self):
        if self.translations_file.exists():
            try:
                payload = read_json_object(self.translations_file)
            except JsonDataError as exc:
                raise RuntimeError(str(exc)) from exc
            for key, translations in payload.items():
                if not isinstance(key, str) or not isinstance(translations, dict):
                    raise RuntimeError(
                        f"Invalid translation entry in {self.translations_file}: {key!r}"
                    )
                if not all(
                    isinstance(lang, str) and isinstance(text, str)
                    for lang, text in translations.items()
                ):
                    raise RuntimeError(
                        f"Invalid translation values in {self.translations_file}: {key!r}"
                    )
            self.translations = payload
        else:
            self.translations = {}

    def _save_translations(self):
        atomic_write_json(self.translations_file, self.translations)

    def t(self, key: str) -> str:
        """
        Uebersetzt einen Key in die aktuelle Sprache.

        Args:
            key: Translation-Key (oft der deutsche Originaltext)

        Returns:
            Uebersetzter Text oder Key als Fallback
        """
        if key in self.translations:
            translated = self.translations[key].get(self.current_lang, "")
            return translated or self.translations[key].get("de", "") or key

        if self._is_german(key):
            self.translations[key] = {
                lang: key if lang == "de" else "" for lang in SUPPORTED_LANGUAGES
            }
            self._save_translations()

        return key

    def set_language(self, lang: str):
        normalized = normalize_language_code(lang)
        if normalized not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language: {lang}")
        self.current_lang = normalized

    def get_language(self) -> str:
        return self.current_lang

    def add_translation(self, key: str, de: str, en: str):
        self.translations[key] = {
            lang: {"de": de, "en": en}.get(lang, "")
            for lang in SUPPORTED_LANGUAGES
        }
        self._save_translations()

    def scan_and_update(self, project_dir: Path = None) -> Dict:
        """Scannt Projekt-Dateien nach deutschen Strings und aktualisiert translations.json."""
        if project_dir is None:
            project_dir = self.app_dir

        found_strings = self._find_german_strings(project_dir)

        added = []
        for string in sorted(found_strings):
            if string not in self.translations:
                self.translations[string] = {
                    lang: string if lang == "de" else ""
                    for lang in SUPPORTED_LANGUAGES
                }
                added.append(string)

        if added:
            self._save_translations()

        missing = [k for k, v in self.translations.items() if not v.get("en")]

        return {'added': added, 'missing': missing, 'total': len(self.translations)}

    def _find_german_strings(self, directory: Path) -> Set[str]:
        german_strings = set()
        skip_dirs = {'build', 'dist', 'venv', '.venv', '__pycache__', 'releases'}

        for py_file in directory.rglob("*.py"):
            if any(folder in py_file.parts for folder in skip_dirs):
                continue
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception:
                continue

            for pattern in self.string_patterns:
                for match in pattern.findall(content):
                    if match and self._is_german(match):
                        german_strings.add(match.strip())

        return german_strings

    def _is_german(self, text: str) -> bool:
        if any(ch in text for ch in "äöüÄÖÜß"):
            return True
        text_lower = text.lower()
        return any(hint in text_lower for hint in self.german_hints)

    def get_missing_translations(self) -> List[str]:
        return [k for k, v in self.translations.items() if not v.get("en")]


if __name__ == "__main__":
    tr = TranslationSystem('de')
    print(f"Sprache: {tr.get_language()}")
    result = tr.scan_and_update()
    print(f"Scan: {result['total']} Strings, {len(result['added'])} neu, {len(result['missing'])} ohne EN")
