#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WikiStub-Seed Pipeline - Vollständiges Wissensdatenbank-Management
=============================================================

Features:
- Markdown → JSON Konvertierung
- JSON → Markdown Export
- Bidirektionale Synchronisation
- Validierung und Konsistenzprüfung
- Statistiken und Reporting
- Tag-Management
"""

import json
import math
import re
import sys
import hashlib
from copy import deepcopy
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone
import argparse

from language_model import (
    DEFAULT_LANGUAGE,
    LOCALIZED_RELEVANCE_FIELD,
    REQUIRED_LANGUAGES,
    SUPPORTED_LANGUAGES,
    get_definition,
    get_relevance,
    existing_mapping_key,
    language_model_metadata,
    merge_entry,
    normalize_entry,
    normalize_localized_map,
    normalize_metawiki_data,
    public_entry,
    identifier_key,
)
from safe_io import (
    JsonDataError,
    atomic_write_json,
    atomic_write_text,
    backup_file,
    read_json_object,
    safe_path_component,
)
from data_policy import duplicate_locations_are_allowed

# ==================== KONFIGURATION ====================

BASE_PATH = Path(__file__).parent.resolve()
JSON_PATH = BASE_PATH / "wikistub_seed.json"
OUTPUT_PATH = BASE_PATH / "output"
BACKUP_PATH = BASE_PATH / "backups"

# Kategorien-Ordner (mit Nummern-Prefix)
CATEGORY_FOLDERS = [
    "01_Mathematik",
    "02_Physik_Astronomie",
    "03_Chemie",
    "04_Biologie_Lebenswissenschaften",
    "05_Medizin_Gesundheit",
    "06_Psychologie_Kognition",
    "07_Informatik_KI",
    "08_Technik_Ingenieurwesen",
    "09_Gesellschaft_Politik",
    "10_Wirtschaft_Recht",
    "11_Geschichte_Archaeologie",
    "12_Kultur_Kunst_Sprache"
]

# Validierungsregeln
MAX_DEFINITION_LENGTH = 500
MIN_DEFINITION_LENGTH = 20
MAX_RELEVANCE_LENGTH = 300
EXCHANGE_SCHEMA = "wikistub-seed-data-v1"
EXCHANGE_LANGUAGES = SUPPORTED_LANGUAGES
EXCHANGE_DEFAULT_PATH = OUTPUT_PATH / f"{EXCHANGE_SCHEMA}.json"


# ==================== DATENKLASSEN ====================

@dataclass
class WikiStub:
    """Ein einzelner Wissenseintrag."""
    title: str
    definition_de: str
    definition_en: str = ""
    relevance: str = ""
    definitions: Dict[str, str] = field(default_factory=dict)
    relevance_i18n: Dict[str, str] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    category: str = ""
    subcategory: str = ""
    source_file: str = ""
    content_hash: str = ""

    def __post_init__(self) -> None:
        self.definitions = normalize_localized_map(
            self.definitions,
            {"de": self.definition_de, "en": self.definition_en},
        )
        self.relevance_i18n = normalize_localized_map(
            self.relevance_i18n,
            {DEFAULT_LANGUAGE: self.relevance},
        )
        self.definition_de = self.definitions["de"]
        self.definition_en = self.definitions["en"]
        self.relevance = self.relevance_i18n[DEFAULT_LANGUAGE]

    def compute_hash(self) -> str:
        """Berechnet einen Hash über den Inhalt."""
        content = f"{self.title}|{self.get_definition('de')}|{self.get_relevance('de')}"
        return hashlib.md5(content.encode()).hexdigest()[:8]

    def to_language_dict(self) -> dict:
        definitions = normalize_localized_map(
            self.definitions,
            {"de": self.definition_de, "en": self.definition_en},
            overwrite_legacy=True,
        )
        relevance_i18n = normalize_localized_map(
            self.relevance_i18n,
            {DEFAULT_LANGUAGE: self.relevance},
            overwrite_legacy=True,
        )
        return {
            "definitions": definitions,
            "definition_de": definitions["de"],
            "definition_en": definitions["en"],
            LOCALIZED_RELEVANCE_FIELD: relevance_i18n,
            "relevance": relevance_i18n[DEFAULT_LANGUAGE],
        }

    def get_definition(self, lang: str = DEFAULT_LANGUAGE) -> str:
        return get_definition(self.to_language_dict(), lang)

    def get_relevance(self, lang: str = DEFAULT_LANGUAGE) -> str:
        return get_relevance(self.to_language_dict(), lang)

    def to_dict(self) -> dict:
        language_fields = self.to_language_dict()
        return public_entry({
            "title": self.title,
            **language_fields,
            "tags": self.tags,
        })

    @classmethod
    def from_dict(cls, data: dict, category: str = "", subcategory: str = "") -> 'WikiStub':
        normalized = normalize_entry(data)
        return cls(
            title=str(normalized.get("title", "")),
            definition_de=str(normalized.get("definition_de", "")),
            definition_en=str(normalized.get("definition_en", "")),
            relevance=str(normalized.get("relevance", "")),
            definitions=normalized.get("definitions", {}),
            relevance_i18n=normalized.get(LOCALIZED_RELEVANCE_FIELD, {}),
            tags=normalized.get("tags", []) if isinstance(normalized.get("tags"), list) else [],
            category=category,
            subcategory=subcategory
        )


@dataclass
class ValidationResult:
    """Ergebnis einer Validierung."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


# ==================== MARKDOWN PARSER ====================

class MarkdownParser:
    """Parst MetaWiki Markdown-Dateien."""

    @staticmethod
    def parse_file(filepath: Path) -> Optional[WikiStub]:
        """Parst eine Markdown-Datei in einen WikiStub."""
        try:
            content = filepath.read_text(encoding="utf-8")
        except FileNotFoundError:
            print(f"  ⚠ Datei nicht gefunden: {filepath}")
            return None
        except (UnicodeDecodeError, OSError) as e:
            print(f"  ⚠ Lesefehler bei {filepath}: {e}")
            return None
        try:
            return MarkdownParser.parse_content(content, str(filepath))
        except (ValueError, SyntaxError) as e:
            print(f"  ⚠ Parse-Fehler in {filepath}: {e}")
            return None
        except Exception as e:
            print(f"  ⚠ Unerwarteter Fehler beim Parsen von {filepath}: {e}")
            return None

    @staticmethod
    def parse_content(content: str, source_file: str = "") -> Optional[WikiStub]:
        """Parst Markdown-Content in einen WikiStub."""
        lines = content.strip().split('\n')

        title = ""
        definition = ""
        definition_en = ""
        definitions = {}
        relevance = ""
        relevance_i18n = {}
        tags = []

        current_section = None
        section_content = []

        for line in lines:
            line = line.strip()

            # Titel (# ...)
            if line.startswith("# ") and not title:
                title = line[2:].strip()
                continue

            # Sektions-Header
            if line.startswith("**") and line.endswith(":**"):
                # Speichere vorherige Sektion
                if current_section and section_content:
                    text = ' '.join(section_content).strip()
                    if current_section == "kurzdefinition":
                        definition = text
                    elif current_section == "definition (de)":
                        definition = text
                    elif current_section == "definition (en)":
                        definition_en = text
                    elif current_section.startswith("definition (") and current_section.endswith(")"):
                        language = current_section[12:-1]
                        if language in SUPPORTED_LANGUAGES:
                            definitions[language] = text
                    elif current_section == "relevanz":
                        relevance = text
                    elif current_section.startswith("relevanz (") and current_section.endswith(")"):
                        language = current_section[10:-1]
                        if language in SUPPORTED_LANGUAGES:
                            relevance_i18n[language] = text
                    elif current_section == "tags":
                        tags = [tag.strip() for tag in text.split(",") if tag.strip()]

                # Neue Sektion
                header = line[2:-3].lower()
                current_section = header
                section_content = []
                continue

            # Inhalt sammeln
            if current_section and line:
                section_content.append(line)

        # Letzte Sektion speichern
        if current_section and section_content:
            text = ' '.join(section_content).strip()
            if current_section == "kurzdefinition":
                definition = text
            elif current_section == "definition (de)":
                definition = text
            elif current_section == "definition (en)":
                definition_en = text
            elif current_section.startswith("definition (") and current_section.endswith(")"):
                language = current_section[12:-1]
                if language in SUPPORTED_LANGUAGES:
                    definitions[language] = text
            elif current_section == "relevanz":
                relevance = text
            elif current_section.startswith("relevanz (") and current_section.endswith(")"):
                language = current_section[10:-1]
                if language in SUPPORTED_LANGUAGES:
                    relevance_i18n[language] = text
            elif current_section == "tags":
                tags = [tag.strip() for tag in text.split(",") if tag.strip()]

        if not title:
            return None

        # Bereinige unerwünschte Zeichen (z.B. 同期)
        definition = MarkdownParser._clean_text(definition)
        relevance = MarkdownParser._clean_text(relevance)
        definitions = {
            language: MarkdownParser._clean_text(text)
            for language, text in definitions.items()
        }
        relevance_i18n = {
            language: MarkdownParser._clean_text(text)
            for language, text in relevance_i18n.items()
        }

        # Extrahiere Kategorie/Subkategorie aus Pfad
        cat, subcat = MarkdownParser._extract_category_from_path(source_file)

        # Tags aus Kategorie generieren
        if cat and not tags:
            tags = [cat.replace("_", " ").lstrip("0123456789_")]
            if subcat:
                tags.append(subcat.replace("_", " "))

        stub = WikiStub(
            title=title,
            definition_de=definition,
            definition_en=definition_en,
            relevance=relevance,
            definitions=definitions,
            relevance_i18n=relevance_i18n,
            tags=tags,
            category=cat,
            subcategory=subcat,
            source_file=source_file
        )
        stub.content_hash = stub.compute_hash()

        return stub

    @staticmethod
    def _clean_text(text: str) -> str:
        """Normalisiert Leerraum, ohne gültigen Unicode-Inhalt zu löschen."""
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    @staticmethod
    def _extract_category_from_path(filepath: str) -> Tuple[str, str]:
        """Extrahiert Kategorie und Subkategorie aus dem Dateipfad."""
        parts = Path(filepath).parts

        category = ""
        subcategory = ""

        for i, part in enumerate(parts):
            # Suche nach Kategorie-Ordner
            for cat_folder in CATEGORY_FOLDERS:
                if part == cat_folder or part.endswith(cat_folder):
                    category = cat_folder
                    # Nächster Teil ist Subkategorie
                    if i + 1 < len(parts) - 1:  # -1 weil letztes Element die Datei ist
                        subcategory = parts[i + 1]
                    break

        return category, subcategory


# ==================== JSON HANDLER ====================

class JsonHandler:
    """Verwaltet die WikiStub-Seed JSON-Datei."""

    def __init__(self, json_path: Optional[Path] = None):
        self.json_path = json_path or JSON_PATH
        self.data: Dict = {"MetaWiki": {}}

    def load(self, *, allow_missing: bool = False) -> bool:
        """Lädt die JSON-Datei."""
        if not self.json_path.exists():
            if allow_missing:
                self.data = {"MetaWiki": {}}
                return True
            print(f"  ✗ Pflichtdatei nicht gefunden: {self.json_path}")
            return False

        try:
            self.data = read_json_object(self.json_path)
            if not isinstance(self.data.get("MetaWiki"), dict):
                raise JsonDataError("MetaWiki muss ein Objekt sein")
            return True
        except JsonDataError as exc:
            print(f"  ✗ Fehler beim Laden: {exc}")
            return False

    def save(
        self,
        *,
        create_backup: bool = True,
        allow_missing_definition: str | None = None,
    ) -> bool:
        """Speichert die JSON-Datei."""
        try:
            validation_errors, _ = validate_localized_data(
                self.data,
                allow_missing_definition=allow_missing_definition,
            )
            if validation_errors:
                print(
                    "  ✗ Speichern verweigert: "
                    f"{len(validation_errors)} strukturelle Datenfehler."
                )
                return False
            # Backup erstellen
            if create_backup and self.json_path.exists():
                backup_file(
                    self.json_path,
                    BACKUP_PATH,
                    prefix="wikistub_seed",
                    keep=10,
                )

            atomic_write_json(self.json_path, self.data)

            return True
        except Exception as e:
            print(f"  ✗ Fehler beim Speichern: {e}")
            return False

    def add_stub(self, stub: WikiStub) -> bool:
        """Fügt einen Stub hinzu."""
        if not stub.title.strip() or not stub.category.strip() or not stub.subcategory.strip():
            return False
        if not isinstance(self.data.get("MetaWiki"), dict):
            return False

        root = self.data["MetaWiki"]

        # Kategorie
        category = existing_mapping_key(root, stub.category)
        if category not in root:
            root[category] = {}
        elif not isinstance(root[category], dict):
            return False

        # Subkategorie
        subcategory = existing_mapping_key(root[category], stub.subcategory)
        if subcategory not in root[category]:
            root[category][subcategory] = []
        elif not isinstance(root[category][subcategory], list):
            return False

        # Prüfe auf Duplikate
        existing = root[category][subcategory]
        for i, item in enumerate(existing):
            if identifier_key(item.get("title", "")) == identifier_key(stub.title):
                existing[i] = merge_entry(item, stub.to_dict())
                return True

        # Neu hinzufügen
        existing.append(stub.to_dict())
        return True

    def get_all_stubs(self) -> List[WikiStub]:
        """Gibt alle Stubs zurück."""
        stubs = []

        if "MetaWiki" not in self.data:
            return stubs

        for category, subcats in self.data["MetaWiki"].items():
            if not isinstance(subcats, dict):
                continue
            for subcategory, items in subcats.items():
                if not isinstance(items, list):
                    continue
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    stub = WikiStub.from_dict(item, category, subcategory)
                    stubs.append(stub)

        return stubs

    def get_statistics(self) -> Dict:
        """Gibt Statistiken zurück."""
        stubs = self.get_all_stubs()

        categories = {}
        tags = {}

        for stub in stubs:
            # Kategorien zählen
            if stub.category not in categories:
                categories[stub.category] = {"total": 0, "subcategories": {}}
            categories[stub.category]["total"] += 1

            if stub.subcategory not in categories[stub.category]["subcategories"]:
                categories[stub.category]["subcategories"][stub.subcategory] = 0
            categories[stub.category]["subcategories"][stub.subcategory] += 1

            # Tags zählen
            for tag in stub.tags:
                tags[tag] = tags.get(tag, 0) + 1

        return {
            "total_stubs": len(stubs),
            "categories": len(categories),
            "category_details": categories,
            "unique_tags": len(tags),
            "tag_frequency": dict(sorted(tags.items(), key=lambda x: -x[1])[:20])
        }


# ==================== MARKDOWN GENERATOR ====================

class MarkdownGenerator:
    """Generiert Markdown-Dateien aus Stubs."""

    @staticmethod
    def generate(
        stub: WikiStub,
        include_english: bool = False,
        language: str = DEFAULT_LANGUAGE,
    ) -> str:
        """Generiert Markdown-Content."""
        cat_display = stub.category.lstrip("0123456789_").replace("_", " ")
        subcat_display = stub.subcategory.replace("_", " ")

        definition_label = (
            "Kurzdefinition" if language == "de" else f"Definition ({language.upper()})"
        )
        relevance_label = (
            "Relevanz" if language == "de" else f"Relevanz ({language.upper()})"
        )
        lines = [
            f"# {stub.title}",
            "",
            f"**{definition_label}:**",
            stub.get_definition(language),
            "",
            "**Kategorie:**",
            f"{cat_display} → {subcat_display}",
            "",
            f"**{relevance_label}:**",
            stub.get_relevance(language),
            ""
        ]

        if language != "de":
            lines.extend([
                "**Definition (DE):**",
                stub.get_definition("de"),
                "",
                "**Relevanz (DE):**",
                stub.get_relevance("de"),
                "",
            ])

        english_definition = stub.get_definition("en")
        if include_english and language != "en" and english_definition:
            lines.extend([
                "**Definition (EN):**",
                english_definition,
                ""
            ])

        if stub.tags:
            lines.extend([
                "**Tags:**",
                ", ".join(stub.tags),
                ""
            ])

        return "\n".join(lines)

    @staticmethod
    def write_file(
        stub: WikiStub,
        output_dir: Path,
        include_english: bool = False,
        language: str = DEFAULT_LANGUAGE,
    ) -> bool:
        """Schreibt eine Markdown-Datei."""
        try:
            # Ordnerstruktur
            folder = (
                output_dir
                / safe_path_component(stub.category)
                / safe_path_component(stub.subcategory)
            )
            folder.mkdir(parents=True, exist_ok=True)

            # Dateiname
            safe_title = safe_path_component(stub.title.replace(" ", "_"))
            filepath = folder / f"{safe_title}.md"

            # Inhalt generieren
            content = MarkdownGenerator.generate(stub, include_english, language)

            # Schreiben
            atomic_write_text(filepath, content)
            return True

        except Exception as e:
            print(f"  ✗ Fehler beim Schreiben von {stub.title}: {e}")
            return False


# ==================== VALIDATOR ====================

class Validator:
    """Validiert MetaWiki-Einträge."""

    @staticmethod
    def validate_stub(stub: WikiStub) -> ValidationResult:
        """Validiert einen einzelnen Stub."""
        errors = []
        warnings = []

        # Titel
        if not stub.title:
            errors.append("Titel fehlt")
        elif len(stub.title) > 100:
            warnings.append(f"Titel zu lang ({len(stub.title)} Zeichen)")

        # Definition
        definition_de = stub.get_definition("de")
        definition_en = stub.get_definition("en")
        relevance_de = stub.get_relevance("de")

        if not definition_de:
            errors.append("Definition fehlt")
        elif len(definition_de) < MIN_DEFINITION_LENGTH:
            warnings.append(f"Definition zu kurz ({len(definition_de)} < {MIN_DEFINITION_LENGTH})")
        elif len(definition_de) > MAX_DEFINITION_LENGTH:
            warnings.append(f"Definition zu lang ({len(definition_de)} > {MAX_DEFINITION_LENGTH})")

        if not definition_en:
            warnings.append("Englische Definition fehlt")

        # Relevanz
        if not relevance_de:
            warnings.append("Relevanz fehlt")
        elif len(relevance_de) > MAX_RELEVANCE_LENGTH:
            warnings.append(f"Relevanz zu lang ({len(relevance_de)} > {MAX_RELEVANCE_LENGTH})")

        # Kategorie
        if not stub.category:
            warnings.append("Kategorie fehlt")

        # Tags
        if not stub.tags:
            warnings.append("Keine Tags")

        # Sonderzeichen prüfen
        if re.search(r'[^\x00-\x7F]', definition_de[-10:] if len(definition_de) > 10 else definition_de):
            # Erlaube Umlaute, aber warnt bei anderen Zeichen
            non_latin = re.findall(r'[^\x00-\xFF]', definition_de)
            if non_latin:
                warnings.append(f"Unerwartete Zeichen: {non_latin}")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    @staticmethod
    def find_duplicates(stubs: List[WikiStub]) -> List[Tuple[WikiStub, WikiStub]]:
        """Findet Duplikate basierend auf Titel."""
        duplicates = []
        seen = {}

        for stub in stubs:
            title_lower = stub.title.lower()
            if title_lower in seen:
                duplicates.append((seen[title_lower], stub))
            else:
                seen[title_lower] = stub

        return duplicates


# ==================== PIPELINE COMMANDS ====================

def count_wrapped_stubs(data: Dict) -> int:
    """Zählt Stubs innerhalb der MetaWiki-Wurzelstruktur."""
    total = 0

    root = data.get("MetaWiki")
    if not isinstance(root, dict):
        return total

    for subcategories in root.values():
        if not isinstance(subcategories, dict):
            continue
        for items in subcategories.values():
            if isinstance(items, list):
                total += len(items)

    return total


def build_exchange_payload(data: Dict, source: str = "wikistub_seed.json") -> Dict:
    """Erzeugt die stabile Austauschhülle für WikiStub-Seed-Daten."""
    normalized_data = normalize_metawiki_data(data)
    return {
        "schema": EXCHANGE_SCHEMA,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "source": source,
        "languages": EXCHANGE_LANGUAGES,
        "language_model": language_model_metadata(),
        "stub_count": count_wrapped_stubs(normalized_data),
        "data": normalized_data,
    }


def validate_localized_data(
    data: Dict,
    *,
    allow_missing_definition: str | None = None,
) -> Tuple[List[str], List[str]]:
    """Validiert Pflichttexte und optionale Sprachmaps in WikiStub-Seed-Daten."""
    errors: List[str] = []
    warnings: List[str] = []
    title_locations: Dict[str, List[Tuple[str, str, str]]] = {}
    root = data.get("MetaWiki")
    if not isinstance(root, dict):
        errors.append("MetaWiki fehlt oder ist kein Objekt.")
        return errors, warnings

    for category, subcategories in root.items():
        if not isinstance(category, str) or not category.strip():
            errors.append("Kategorienamen müssen nichtleere Strings sein.")
            continue
        if not isinstance(subcategories, dict):
            errors.append(f"{category}: Kategorieinhalt muss ein Objekt sein.")
            continue
        for subcategory, entries in subcategories.items():
            if not isinstance(subcategory, str) or not subcategory.strip():
                errors.append(f"{category}: Subkategorienamen müssen Strings sein.")
                continue
            if not isinstance(entries, list):
                errors.append(
                    f"{category}/{subcategory}: Subkategorieinhalt muss eine Liste sein."
                )
                continue
            for index, entry in enumerate(entries):
                if not isinstance(entry, dict):
                    errors.append(f"{category}/{subcategory}[{index}] ist kein Objekt.")
                    continue
                label = f"{category}/{subcategory}/{entry.get('title', index)}"
                title = entry.get("title")
                if not isinstance(title, str) or not title.strip():
                    errors.append(f"{category}/{subcategory}[{index}]: Titel fehlt oder ist leer.")
                else:
                    title_locations.setdefault(identifier_key(title), []).append(
                        (category, subcategory, title)
                    )
                if "definitions" in entry and not isinstance(entry["definitions"], dict):
                    errors.append(f"{label}: definitions muss ein Objekt sein.")
                if LOCALIZED_RELEVANCE_FIELD in entry and not isinstance(entry[LOCALIZED_RELEVANCE_FIELD], dict):
                    errors.append(f"{label}: {LOCALIZED_RELEVANCE_FIELD} muss ein Objekt sein.")
                tags = entry.get("tags", [])
                if not isinstance(tags, list) or not all(
                    isinstance(tag, str) and tag.strip() for tag in tags
                ):
                    errors.append(f"{label}: tags muss eine Liste nichtleerer Strings sein.")

                normalized = normalize_entry(entry)
                definitions = normalized["definitions"]
                for required_language in REQUIRED_LANGUAGES:
                    if (
                        required_language != allow_missing_definition
                        and not definitions.get(required_language, "").strip()
                    ):
                        errors.append(
                            f"{label}: Definition für {required_language} fehlt."
                        )

    for locations in title_locations.values():
        if len(locations) <= 1:
            continue
        title = locations[0][2]
        if not duplicate_locations_are_allowed(
            title, ((category, subcategory) for category, subcategory, _ in locations)
        ):
            errors.append(f"{title}: unerwartete domänenübergreifende Doppelbezeichnung.")

    return errors, warnings


def validate_exchange_payload(payload: object) -> ValidationResult:
    """Validiert die Exporthülle `wikistub-seed-data-v1`."""
    errors: List[str] = []
    warnings: List[str] = []

    if not isinstance(payload, dict):
        return ValidationResult(False, ["Top-Level muss ein JSON-Objekt sein."], warnings)

    schema = payload.get("schema")
    if schema != EXCHANGE_SCHEMA:
        errors.append(f"schema muss '{EXCHANGE_SCHEMA}' sein.")  # wikistub-seed-data-v1

    generated_at = payload.get("generated_at")
    if not isinstance(generated_at, str):
        errors.append("generated_at fehlt oder ist kein String.")
    else:
        try:
            parsed_timestamp = datetime.fromisoformat(
                generated_at.replace("Z", "+00:00")
            )
            if parsed_timestamp.tzinfo is None:
                errors.append("generated_at muss eine Zeitzone enthalten.")
        except ValueError:
            errors.append("generated_at ist kein gültiger ISO-8601-Zeitstempel.")

    source = payload.get("source")
    if not isinstance(source, str) or not source.strip():
        errors.append("source fehlt oder ist leer.")
    elif Path(source).is_absolute():
        warnings.append("source sollte kein absoluter Pfad sein.")

    languages = payload.get("languages")
    if not isinstance(languages, list) or not all(isinstance(lang, str) for lang in languages):
        errors.append("languages muss eine String-Liste sein.")
    else:
        language_set = set(languages)
        if len(language_set) != len(languages):
            errors.append("languages darf keine Duplikate enthalten.")
        missing_required = [lang for lang in REQUIRED_LANGUAGES if lang not in language_set]
        unknown = sorted(language_set - set(EXCHANGE_LANGUAGES))
        missing_supported = [lang for lang in EXCHANGE_LANGUAGES if lang not in language_set]
        if missing_required:
            errors.append(f"languages fehlen Pflichtsprachen: {', '.join(missing_required)}.")
        if unknown:
            warnings.append(f"languages enthält unbekannte Sprachcodes: {', '.join(unknown)}.")
        if missing_supported:
            warnings.append(
                "languages enthält noch nicht alle vorbereiteten Sprachslots "
                f"({', '.join(missing_supported)} fehlen)."
            )

    language_model = payload.get("language_model")
    if language_model is None:
        warnings.append("language_model fehlt; Legacy-Exporte bleiben lesbar, aber nicht vollständig mehrsprachenfähig.")
    elif not isinstance(language_model, dict):
        errors.append("language_model muss ein Objekt sein.")
    else:
        model_languages = language_model.get("languages")
        if model_languages != EXCHANGE_LANGUAGES:
            warnings.append("language_model.languages weicht vom erwarteten WikiStub-Seed-Sprachmodell ab.")

    data = payload.get("data")
    actual_stub_count = None
    if not isinstance(data, dict):
        errors.append("data fehlt oder ist kein Objekt.")
    else:
        root = data.get("MetaWiki")
        if not isinstance(root, dict):
            errors.append("data.MetaWiki fehlt oder ist kein Objekt.")
        else:
            actual_stub_count = count_wrapped_stubs(data)
            language_errors, language_warnings = validate_localized_data(data)
            errors.extend(language_errors)
            warnings.extend(language_warnings)

    stub_count = payload.get("stub_count")
    if (
        not isinstance(stub_count, int)
        or isinstance(stub_count, bool)
        or stub_count < 0
    ):
        errors.append("stub_count fehlt oder ist keine nichtnegative Zahl.")
    elif actual_stub_count is not None and stub_count != actual_stub_count:
        errors.append(
            f"stub_count stimmt nicht mit den tatsächlichen Daten überein ({stub_count} != {actual_stub_count})."
        )

    return ValidationResult(len(errors) == 0, errors, warnings)


def report_invalid_source(
    data: Dict,
    *,
    allow_missing_definition: str | None = None,
) -> bool:
    """Print structural source errors and return whether the dataset is valid."""
    errors, _ = validate_localized_data(
        data,
        allow_missing_definition=allow_missing_definition,
    )
    for error in errors:
        print(f"  ✗ {error}")
    return not errors

def cmd_import(args):
    """Importiert Markdown-Dateien in JSON."""
    print("\n📥 IMPORT: Markdown → JSON")
    print("=" * 50)

    json_handler = JsonHandler()
    if not json_handler.load():
        print("  ✗ JSON-Datei konnte nicht geladen werden. Abbruch.")
        return 1
    if not report_invalid_source(json_handler.data):
        return 1

    original_data = deepcopy(json_handler.data)
    imported = 0
    errors = 0

    # Scanne alle Kategorien
    for category in CATEGORY_FOLDERS:
        cat_path = BASE_PATH / category
        if not cat_path.exists():
            continue

        print(f"\n📁 {category}")

        # Scanne Unterkategorien
        for subcat in cat_path.iterdir():
            if not subcat.is_dir():
                continue

            # Scanne MD-Dateien
            for md_file in subcat.glob("*.md"):
                stub = MarkdownParser.parse_file(md_file)
                if stub:
                    validation = Validator.validate_stub(stub)
                    if not validation.is_valid:
                        errors += 1
                        print(f"  ✗ {md_file.name}: {', '.join(validation.errors)}")
                        continue
                    if json_handler.add_stub(stub):
                        imported += 1
                        print(f"  ✓ {stub.title}")
                    else:
                        errors += 1
                        print(f"  ✗ {md_file.name}: Datenstruktur unvereinbar")
                else:
                    errors += 1
                    print(f"  ✗ {md_file.name}")

    if errors and not args.allow_partial:
        json_handler.data = original_data
        print("  ✗ Import wegen Fehlern verworfen; JSON bleibt unverändert.")
        print(f"\n{'=' * 50}")
        print(f"✗ 0 Stubs gespeichert, {errors} Fehler")
        return 1

    # Speichern
    if imported > 0:
        if not json_handler.save():
            print("  ✗ Speichern fehlgeschlagen!")
            return 1

    print(f"\n{'=' * 50}")
    print(f"✓ {imported} Stubs gespeichert, {errors} Fehler")
    return 1 if errors else 0


def cmd_export(args):
    """Exportiert JSON nach Markdown."""
    print("\n📤 EXPORT: JSON → Markdown")
    print("=" * 50)

    output_dir = OUTPUT_PATH if args.output else BASE_PATH

    json_handler = JsonHandler()
    if not json_handler.load():
        return 1
    if not report_invalid_source(json_handler.data):
        return 1

    stubs = json_handler.get_all_stubs()
    print(f"  Gefunden: {len(stubs)} Stubs")

    exported = 0
    failures = 0
    for stub in stubs:
        if MarkdownGenerator.write_file(
            stub,
            output_dir,
            args.english,
            args.lang,
        ):
            exported += 1
        else:
            failures += 1

    print(f"\n✓ {exported} Dateien exportiert nach {output_dir}")
    return 1 if failures else 0


def cmd_export_data(args):
    """Exportiert die stabile `wikistub-seed-data-v1`-Hülle als JSON."""
    print("\n📦 EXPORT: wikistub-seed-data-v1")
    print("=" * 50)

    output_path = Path(args.path).expanduser() if args.path else EXCHANGE_DEFAULT_PATH
    output_path.parent.mkdir(parents=True, exist_ok=True)

    json_handler = JsonHandler()
    if not json_handler.load():
        print("  ✗ JSON-Datei konnte nicht geladen werden. Abbruch.")
        return 1
    if not report_invalid_source(json_handler.data):
        return 1

    payload = build_exchange_payload(json_handler.data, source=JSON_PATH.name)
    try:
        atomic_write_json(output_path, payload)
    except (OSError, TypeError, ValueError) as exc:
        print(f"  ✗ Export fehlgeschlagen: {exc}")
        return 1

    print(f"  ✓ Schema: {payload['schema']}")
    print(f"  ✓ Stubs: {payload['stub_count']}")
    print(f"  ✓ Datei: {output_path}")
    return 0


def cmd_validate(args):
    """Validiert alle Einträge."""
    if getattr(args, "exchange", None):
        exchange_path = Path(args.exchange).expanduser()

        print("\n🔍 VALIDIERUNG: wikistub-seed-data-v1")
        print("=" * 50)

        if not exchange_path.exists():
            print(f"  ✗ Datei nicht gefunden: {exchange_path}")
            return 1

        try:
            payload = json.loads(exchange_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"  ✗ Exportdatei konnte nicht gelesen werden: {exc}")
            return 1

        result = validate_exchange_payload(payload)

        if result.is_valid:
            print(f"  ✓ Gültige Exporthülle: {exchange_path}")
            print(f"  ✓ Schema: {payload.get('schema')}")
            print(f"  ✓ Stubs: {payload.get('stub_count')}")
        else:
            print(f"  ✗ Ungültige Exporthülle: {exchange_path}")

        for err in result.errors:
            print(f"    ERROR: {err}")

        if args.verbose:
            for warn in result.warnings:
                print(f"    WARN: {warn}")
        elif result.warnings:
            print(f"  ⚠ {len(result.warnings)} Warnung(en) vorhanden. Mit -v anzeigen.")

        return 0 if result.is_valid else 1

    print("\n🔍 VALIDIERUNG")
    print("=" * 50)

    json_handler = JsonHandler()
    if not json_handler.load():
        print("  ✗ JSON-Datei konnte nicht geladen werden. Abbruch.")
        return 1
    structure_errors, structure_warnings = validate_localized_data(json_handler.data)
    if structure_errors:
        for err in structure_errors:
            print(f"    ERROR: {err}")
        return 1
    if args.verbose:
        for warning in structure_warnings:
            print(f"    WARN: {warning}")
    stubs = json_handler.get_all_stubs()

    valid = 0
    with_warnings = 0
    invalid = 0

    for stub in stubs:
        result = Validator.validate_stub(stub)

        if not result.is_valid:
            invalid += 1
            print(f"\n✗ {stub.title}")
            for err in result.errors:
                print(f"    ERROR: {err}")
            for warn in result.warnings:
                print(f"    WARN: {warn}")
        elif result.warnings:
            with_warnings += 1
            if args.verbose:
                print(f"\n⚠ {stub.title}")
                for warn in result.warnings:
                    print(f"    WARN: {warn}")
        else:
            valid += 1

    # Duplikate
    duplicates = Validator.find_duplicates(stubs)
    duplicate_groups: Dict[str, List[WikiStub]] = {}
    for stub in stubs:
        duplicate_groups.setdefault(identifier_key(stub.title), []).append(stub)
    duplicate_groups = {
        title: group for title, group in duplicate_groups.items() if len(group) > 1
    }
    unexpected_duplicates = {
        title: group
        for title, group in duplicate_groups.items()
        if not duplicate_locations_are_allowed(
            group[0].title,
            ((stub.category, stub.subcategory) for stub in group),
        )
    }
    if duplicates:
        print(f"\n⚠ {len(duplicates)} Duplikate gefunden:")
        for stub1, stub2 in duplicates:
            print(f"  - {stub1.title}: {stub1.category}/{stub1.subcategory} vs {stub2.category}/{stub2.subcategory}")

    print(f"\n{'=' * 50}")
    print(f"✓ Gültig: {valid} | ⚠ Mit Warnungen: {with_warnings} | ✗ Ungültig: {invalid}")
    print(f"🔄 Duplikate: {len(duplicates)}")
    if duplicate_groups and not unexpected_duplicates:
        print(f"✓ Geprüfte Querschnitts-Duplikate: {len(duplicate_groups)}")
    if unexpected_duplicates:
        print(f"✗ Unerwartete Duplikatgruppen: {len(unexpected_duplicates)}")
    return 1 if invalid or unexpected_duplicates else 0


def cmd_stats(args):
    """Zeigt Statistiken an."""
    print("\n📊 STATISTIKEN")
    print("=" * 50)

    json_handler = JsonHandler()
    if not json_handler.load():
        print("  ✗ JSON-Datei konnte nicht geladen werden. Abbruch.")
        return 1
    if not report_invalid_source(json_handler.data):
        return 1
    stats = json_handler.get_statistics()

    print("\n📈 Übersicht:")
    print(f"   Gesamt-Stubs: {stats['total_stubs']}")
    print(f"   Kategorien: {stats['categories']}")
    print(f"   Eindeutige Tags: {stats['unique_tags']}")

    print("\n📁 Kategorien:")
    for cat, details in sorted(stats['category_details'].items()):
        print(f"   {cat}: {details['total']} Stubs")
        if args.verbose:
            for subcat, count in details['subcategories'].items():
                print(f"      └─ {subcat}: {count}")

    print("\n🏷 Top Tags:")
    for tag, count in list(stats['tag_frequency'].items())[:10]:
        print(f"   {tag}: {count}")
    return 0


def cmd_sync(args):
    """Bidirektionale Synchronisation."""
    print("\n🔄 SYNCHRONISATION")
    print("=" * 50)

    # Erst Import
    print("\n1️⃣ Importiere neue Markdown-Dateien...")

    json_handler = JsonHandler()
    if not json_handler.load():
        print("  ✗ JSON-Datei konnte nicht geladen werden. Abbruch.")
        return 1
    if not report_invalid_source(json_handler.data):
        return 1
    original_data = deepcopy(json_handler.data)
    existing_locations = {
        (identifier_key(s.category), identifier_key(s.subcategory), s.title.strip().casefold())
        for s in json_handler.get_all_stubs()
    }

    new_stubs = 0
    errors = 0

    for category in CATEGORY_FOLDERS:
        cat_path = BASE_PATH / category
        if not cat_path.exists():
            continue

        for subcat in cat_path.iterdir():
            if not subcat.is_dir():
                continue

            for md_file in subcat.glob("*.md"):
                stub = MarkdownParser.parse_file(md_file)
                location = (
                    identifier_key(stub.category) if stub else "",
                    identifier_key(stub.subcategory) if stub else "",
                    stub.title.strip().casefold() if stub else "",
                )
                if not stub:
                    errors += 1
                    print(f"  ✗ {md_file.name}: nicht parsebar")
                elif location not in existing_locations:
                    validation = Validator.validate_stub(stub)
                    if validation.is_valid and json_handler.add_stub(stub):
                        existing_locations.add(location)
                        new_stubs += 1
                        print(f"  + {stub.title}")
                    else:
                        errors += 1
                        print(f"  ✗ {md_file.name}: ungültiger Stub")

    if errors:
        json_handler.data = original_data
        print("  ✗ Synchronisation wegen Fehlern verworfen.")
        return 1

    if new_stubs > 0:
        if not json_handler.save():
            print("  ✗ Speichern fehlgeschlagen!")
            return 1

    print(f"\n   ✓ {new_stubs} neue Stubs importiert")

    # Dann Export (wenn gewünscht)
    if args.export:
        print("\n2️⃣ Exportiere nach Markdown...")
        stubs = json_handler.get_all_stubs()
        exported = sum(
            MarkdownGenerator.write_file(stub, OUTPUT_PATH, language=args.lang)
            for stub in stubs
        )
        print(f"   ✓ {exported} Dateien exportiert")
        if exported != len(stubs):
            return 1
    return 0


def cmd_translate(args):
    """Übersetzt fehlende Definitionen in eine unterstützte Zielsprache."""
    print("\n🌐 ÜBERSETZUNG")
    print("=" * 50)

    limit = getattr(args, "limit", None)
    if not isinstance(limit, int) or limit <= 0:
        print("  ✗ Eine positive --limit-Grenze ist für API-Läufe erforderlich.")
        return 1
    if not getattr(args, "confirm_api_cost", False):
        print("  ✗ API-Kosten nicht bestätigt; nutze zusätzlich --confirm-api-cost.")
        return 1
    max_budget_usd = getattr(args, "max_budget_usd", None)
    if (
        not isinstance(max_budget_usd, (int, float))
        or not math.isfinite(max_budget_usd)
        or max_budget_usd <= 0
    ):
        print("  ✗ Eine positive --max-budget-usd-Kostengrenze ist erforderlich.")
        return 1
    target_language = args.lang

    try:
        from translate import estimate_batch_max_cost_usd, translate_text, is_available
    except ImportError:
        print("  ✗ translate.py nicht gefunden.")
        return 1

    if not is_available():
        print("  ✗ Übersetzung nicht verfügbar.")
        print("  Bitte setze ANTHROPIC_API_KEY und installiere: pip install anthropic")
        return 1

    import time

    json_handler = JsonHandler()
    if not json_handler.load():
        print("  ✗ JSON-Datei konnte nicht geladen werden. Abbruch.")
        return 1
    if not report_invalid_source(
        json_handler.data,
        allow_missing_definition=target_language,
    ):
        return 1
    stubs = json_handler.get_all_stubs()

    to_translate = [
        stub
        for stub in stubs
        if not stub.definitions.get(target_language, "").strip()
    ]
    total = len(to_translate)

    if limit < total:
        to_translate = to_translate[:limit]

    projected_cost = estimate_batch_max_cost_usd(
        [stub.get_definition("de") for stub in to_translate],
        target_language,
    )
    if projected_cost > max_budget_usd:
        print(
            f"  ✗ Maximale Laufkosten ${projected_cost:.6f} überschreiten "
            f"Budget ${max_budget_usd:.6f}."
        )
        return 1

    print(f"  Gesamt ohne Übersetzung: {total}")
    print(f"  Zu übersetzen: {len(to_translate)}")
    print(f"  Kostenobergrenze dieses Laufs: ${projected_cost:.6f}")

    translated = 0
    errors = 0
    checkpoint_saved = False
    delay = args.delay
    if not math.isfinite(delay) or delay < 0:
        print("  ✗ --delay muss endlich und nichtnegativ sein.")
        return 1

    for i, stub in enumerate(to_translate):
        result = translate_text(stub.get_definition("de"), target_language)
        if result:
            stub.definitions[target_language] = result
            if target_language == "en":
                stub.definition_en = result
            json_handler.add_stub(stub)
            if not json_handler.save(
                create_backup=not checkpoint_saved,
                allow_missing_definition=target_language,
            ):
                print("  ✗ Atomares Zwischenspeichern fehlgeschlagen; Lauf abgebrochen.")
                return 1
            checkpoint_saved = True
            translated += 1
            print(f"  ✓ {stub.title}")
            # Nur nach erfolgreichen API-Calls schlafen (Fehler verbrauchen kein Rate-Limit)
            if delay > 0 and i < len(to_translate) - 1:
                time.sleep(delay)
        else:
            errors += 1
            print(f"  ✗ {stub.title}")

    print(f"\n{'=' * 50}")
    print(f"✓ {translated} übersetzt und einzeln gespeichert, {errors} Fehler")
    return 1 if errors else 0


def cmd_clean(args):
    """Bereinigt Daten (Encoding-Fehler, etc.)."""
    print("\n🧹 BEREINIGUNG")
    print("=" * 50)

    json_handler = JsonHandler()
    if not json_handler.load():
        print("  ✗ JSON-Datei konnte nicht geladen werden. Abbruch.")
        return 1
    if not report_invalid_source(json_handler.data):
        return 1
    stubs = json_handler.get_all_stubs()

    cleaned = 0

    for stub in stubs:
        original_dict = stub.to_dict()

        # Bereinige
        stub.definition_de = MarkdownParser._clean_text(stub.get_definition("de"))
        stub.relevance = MarkdownParser._clean_text(stub.get_relevance("de"))
        stub.definitions["de"] = stub.definition_de
        stub.relevance_i18n[DEFAULT_LANGUAGE] = stub.relevance

        if stub.to_dict() != original_dict:
            cleaned += 1
            print(f"  🧹 {stub.title}")
            json_handler.add_stub(stub)

    if cleaned > 0:
        if not json_handler.save():
            print("  ✗ Speichern fehlgeschlagen!")
            return 1

    print(f"\n✓ {cleaned} Einträge bereinigt")
    return 0


# ==================== MAIN ====================

def configure_console_output() -> None:
    """Prevent status glyphs from crashing redirected legacy Windows consoles."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(errors="replace")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="WikiStub-Seed Pipeline - Wissensdatenbank-Management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  python wikistub_seed_pipeline.py import          # Markdown → JSON
  python wikistub_seed_pipeline.py export          # JSON → Markdown
  python wikistub_seed_pipeline.py export-data     # JSON → wikistub-seed-data-v1
  python wikistub_seed_pipeline.py validate -v     # Validierung (verbose)
  python wikistub_seed_pipeline.py validate --exchange output/wikistub-seed-data-v1.json
  python wikistub_seed_pipeline.py stats -v        # Statistiken (detailliert)
  python wikistub_seed_pipeline.py sync            # Bidirektionale Sync
  python wikistub_seed_pipeline.py clean           # Daten bereinigen
  python wikistub_seed_pipeline.py translate       # Englische Übersetzungen ergänzen
  python wikistub_seed_pipeline.py translate -l 50 # Maximal 50 Stubs übersetzen
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Verfügbare Befehle")

    # Import
    p_import = subparsers.add_parser("import", help="Importiere Markdown → JSON")
    p_import.add_argument(
        "--allow-partial",
        action="store_true",
        help="Speichert valide Teilmengen trotz fehlerhafter Markdown-Dateien",
    )
    p_import.set_defaults(func=cmd_import)

    # Export
    p_export = subparsers.add_parser("export", help="Exportiere JSON → Markdown")
    p_export.add_argument("--output", "-o", action="store_true", help="In output/ exportieren")
    p_export.add_argument("--english", "-e", action="store_true", help="Englische Übersetzung inkludieren")
    p_export.add_argument(
        "--lang",
        choices=SUPPORTED_LANGUAGES,
        default=DEFAULT_LANGUAGE,
        help="Sprache des primären Exports",
    )
    p_export.set_defaults(func=cmd_export)

    # Export data
    p_export_data = subparsers.add_parser("export-data", help="Exportiere JSON → wikistub-seed-data-v1")
    p_export_data.add_argument("--path", help="Zielpfad für die Exporthülle")
    p_export_data.set_defaults(func=cmd_export_data)

    # Validate
    p_validate = subparsers.add_parser("validate", help="Validiere Einträge")
    p_validate.add_argument("--exchange", help="Pfad zu einer wikistub-seed-data-v1-Datei")
    p_validate.add_argument("--verbose", "-v", action="store_true", help="Zeige auch Warnungen")
    p_validate.set_defaults(func=cmd_validate)

    # Stats
    p_stats = subparsers.add_parser("stats", help="Zeige Statistiken")
    p_stats.add_argument("--verbose", "-v", action="store_true", help="Detaillierte Ausgabe")
    p_stats.set_defaults(func=cmd_stats)

    # Sync
    p_sync = subparsers.add_parser("sync", help="Bidirektionale Synchronisation")
    p_sync.add_argument("--export", "-e", action="store_true", help="Auch nach Markdown exportieren")
    p_sync.add_argument(
        "--lang",
        choices=SUPPORTED_LANGUAGES,
        default=DEFAULT_LANGUAGE,
        help="Sprache eines optionalen Exports",
    )
    p_sync.set_defaults(func=cmd_sync)

    # Clean
    p_clean = subparsers.add_parser("clean", help="Bereinige Daten")
    p_clean.set_defaults(func=cmd_clean)

    # Translate
    p_translate = subparsers.add_parser("translate", help="Übersetze Stubs via Claude API")
    p_translate.add_argument("--limit", "-l", type=int, help="Maximale Anzahl kostenpflichtiger API-Aufrufe")
    p_translate.add_argument(
        "--confirm-api-cost",
        action="store_true",
        help="Bestätigt ausdrücklich, dass der begrenzte API-Lauf Kosten verursachen darf",
    )
    p_translate.add_argument(
        "--max-budget-usd",
        type=float,
        help="Explizite konservative Kostenobergrenze in USD",
    )
    p_translate.add_argument(
        "--lang",
        choices=[lang for lang in SUPPORTED_LANGUAGES if lang != DEFAULT_LANGUAGE],
        default="en",
        help="Zielsprache",
    )
    p_translate.add_argument(
        "--delay",
        type=float,
        default=0.3,
        help="Pause in Sekunden zwischen erfolgreichen API-Aufrufen",
    )
    p_translate.set_defaults(func=cmd_translate)

    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    print(f"\n{'='*60}")
    print("  WikiStub-Seed Pipeline v2.0")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

    exit_code = args.func(args)

    print(f"\n{'='*60}")
    print("  Fertig!")
    print(f"{'='*60}\n")

    return exit_code if isinstance(exit_code, int) else 0


if __name__ == "__main__":
    configure_console_output()
    sys.exit(main())
