#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
md_to_json.py - Markdown zu JSON Konverter für WikiStub-Seed
=========================================================

Parst alle vorhandenen MD-Dateien aus den Kategorieordnern
und erstellt/aktualisiert JSON-Einträge in wikistub_seed.json.

Nutzung:
    python md_to_json.py                  # Alle MD-Dateien konvertieren
    python md_to_json.py --dry-run        # Nur anzeigen, nicht speichern
    python md_to_json.py --category 07    # Nur eine Kategorie
"""

import re
import sys
from copy import deepcopy
from pathlib import Path
from datetime import datetime

from language_model import (
    LOCALIZED_RELEVANCE_FIELD,
    SUPPORTED_LANGUAGES,
    existing_mapping_key,
    identifier_key,
    merge_entry,
    normalize_entry,
    public_entry,
)
from safe_io import JsonDataError, atomic_write_json, backup_file, read_json_object

BASE_PATH = Path(__file__).parent.resolve()
JSON_PATH = BASE_PATH / "wikistub_seed.json"
BACKUP_PATH = BASE_PATH / "backups"

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


def clean_text(text):
    """Normalisiert Leerraum, ohne gültigen Unicode-Inhalt zu löschen."""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def parse_md_file(filepath):
    """Parst eine einzelne Markdown-Datei und gibt ein Stub-Dict zurück."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  FEHLER beim Lesen von {filepath}: {e}")
        return None

    lines = content.strip().split('\n')

    title = ""
    definition = ""
    definition_en = ""
    definitions = {}
    relevance = ""
    relevance_i18n = {}
    tags = []

    current_section = None
    section_lines = []

    for line in lines:
        stripped = line.strip()

        # Titel
        if stripped.startswith("# ") and not title:
            title = stripped[2:].strip()
            continue

        # Sektions-Header: **XYZ:**
        if stripped.startswith("**") and stripped.endswith(":**"):
            # Vorherige Sektion speichern
            if current_section and section_lines:
                text = ' '.join(section_lines).strip()
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

            header = stripped[2:-3].lower()
            current_section = header
            section_lines = []
            continue

        # Inline-Format: **XYZ:** Inhalt auf gleicher Zeile
        match = re.match(r'\*\*(.+?):\*\*\s*(.*)', stripped)
        if match:
            header = match.group(1).lower()
            inline_text = match.group(2).strip()
            if header == "kurzdefinition" and inline_text:
                definition = inline_text
                current_section = None
                continue
            elif header == "relevanz" and inline_text:
                relevance = inline_text
                current_section = None
                continue
            elif header.startswith("definition") and "(de)" in header and inline_text:
                definition = inline_text
                current_section = None
                continue
            elif header.startswith("definition") and "(en)" in header and inline_text:
                definition_en = inline_text
                current_section = None
                continue
            elif header.startswith("definition") and inline_text:
                language = header.removeprefix("definition").strip(" ()")
                if language in SUPPORTED_LANGUAGES:
                    definitions[language] = inline_text
                    current_section = None
                    continue
            elif header.startswith("relevanz") and inline_text:
                language = header.removeprefix("relevanz").strip(" ()")
                if language in SUPPORTED_LANGUAGES:
                    relevance_i18n[language] = inline_text
                    current_section = None
                    continue
            elif header == "tags" and inline_text:
                tags = [tag.strip() for tag in inline_text.split(",") if tag.strip()]
                current_section = None
                continue

        # Inhalt sammeln
        if current_section and stripped:
            section_lines.append(stripped)

    # Letzte Sektion
    if current_section and section_lines:
        text = ' '.join(section_lines).strip()
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

    # Bereinigen
    definition = clean_text(definition)
    relevance = clean_text(relevance)

    # Kategorie/Subkategorie aus Dateipfad extrahieren
    parts = filepath.parts
    cat = ""
    subcat = ""
    for i, part in enumerate(parts):
        for cat_folder in CATEGORY_FOLDERS:
            if part == cat_folder:
                cat = cat_folder
                if i + 1 < len(parts) - 1:
                    subcat = parts[i + 1]
                break

    # Tags generieren
    if cat and not tags:
        tag_name = cat.lstrip("0123456789_").replace("_", " ")
        tags.append(tag_name)
        if subcat:
            tags.append(subcat.replace("_", " "))

    return normalize_entry({
        "title": title,
        "definition_de": definition,
        "definition_en": clean_text(definition_en),
        "definitions": {
            language: clean_text(text) for language, text in definitions.items()
        },
        "relevance": relevance,
        LOCALIZED_RELEVANCE_FIELD: {
            language: clean_text(text)
            for language, text in relevance_i18n.items()
        },
        "tags": tags,
        "_category": cat,
        "_subcategory": subcat
    })


def load_json():
    """Lädt die bestehende Pflichtdatei fail-closed."""
    try:
        data = read_json_object(JSON_PATH)
    except JsonDataError as exc:
        print(f"FEHLER beim Lesen der JSON: {exc}")
        return None
    root = data.get("MetaWiki")
    if not isinstance(root, dict):
        print("FEHLER beim Lesen der JSON: MetaWiki muss ein Objekt sein.")
        return None
    for category, subcategories in root.items():
        if not isinstance(category, str) or not isinstance(subcategories, dict):
            print("FEHLER beim Lesen der JSON: Kategorien müssen Objekte sein.")
            return None
        for subcategory, entries in subcategories.items():
            if not isinstance(subcategory, str) or not isinstance(entries, list):
                print(f"FEHLER: Ungültige Subkategorie in {category}.")
                return None
            if any(not isinstance(entry, dict) for entry in entries):
                print(f"FEHLER: Ungültiger Stub in {category}/{subcategory}.")
                return None
    return data


def save_json(data, dry_run=False):
    """Speichert wikistub_seed.json mit Backup."""
    if dry_run:
        print("\n[DRY-RUN] Keine Änderungen gespeichert.")
        return

    # Backup
    if JSON_PATH.exists():
        backup_file(JSON_PATH, BACKUP_PATH, prefix="wikistub_seed", keep=10)

    atomic_write_json(JSON_PATH, data)


def add_stub_to_data(data, stub_dict):
    """Fuegt einen Stub in die JSON-Struktur ein."""
    incoming = dict(stub_dict)
    cat = incoming.pop("_category", "")
    subcat = incoming.pop("_subcategory", "")

    if not cat:
        cat = "00_Unsortiert"
    if not subcat:
        subcat = "Allgemein"

    root = data.get("MetaWiki")
    if not isinstance(root, dict):
        raise ValueError("MetaWiki muss ein Objekt sein")
    category = existing_mapping_key(root, cat)
    if category not in root:
        root[category] = {}
    elif not isinstance(root[category], dict):
        raise ValueError(f"Kategorie {category} muss ein Objekt sein")
    subcategory = existing_mapping_key(root[category], subcat)
    if subcategory not in root[category]:
        root[category][subcategory] = []
    elif not isinstance(root[category][subcategory], list):
        raise ValueError(f"Subkategorie {category}/{subcategory} muss eine Liste sein")

    # Duplikat-Pruefung innerhalb der gleichen Subkategorie
    existing = root[category][subcategory]
    for i, item in enumerate(existing):
        if identifier_key(item.get("title", "")) == identifier_key(incoming["title"]):
            existing[i] = merge_entry(item, incoming)
            return "updated"

    existing.append(public_entry(incoming))
    return "added"


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description="WikiStub-Seed: Markdown zu JSON Konverter")
    parser.add_argument("--dry-run", action="store_true", help="Nur anzeigen, nicht speichern")
    parser.add_argument("--category", type=str, help="Nur bestimmte Kategorie (z.B. '07')")
    parser.add_argument(
        "--allow-partial",
        action="store_true",
        help="Speichert valide Teilmengen trotz fehlerhafter Markdown-Dateien",
    )
    args = parser.parse_args(argv)

    print("=" * 60)
    print("  WikiStub-Seed: Markdown -> JSON Konverter")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    data = load_json()
    if data is None:
        return 1
    original_data = deepcopy(data)

    # Kategorien filtern
    categories = CATEGORY_FOLDERS
    if args.category:
        categories = [c for c in categories if c.startswith(args.category)]
        if not categories:
            print(f"Keine Kategorie mit Prefix '{args.category}' gefunden.")
            return 1

    total_added = 0
    total_updated = 0
    total_errors = 0

    for category in categories:
        cat_path = BASE_PATH / category
        if not cat_path.exists():
            continue

        print(f"\n[{category}]")

        for subcat_dir in sorted(cat_path.iterdir()):
            if not subcat_dir.is_dir():
                continue

            md_files = list(subcat_dir.glob("*.md"))
            if not md_files:
                continue

            for md_file in sorted(md_files):
                stub = parse_md_file(md_file)
                if stub:
                    try:
                        result = add_stub_to_data(data, stub)
                    except (KeyError, TypeError, ValueError) as exc:
                        total_errors += 1
                        print(f"  ! Fehler: {md_file.name}: {exc}")
                        continue
                    if result == "added":
                        total_added += 1
                        print(f"  + {stub.get('title', '?')}")
                    else:
                        total_updated += 1
                        print(f"  ~ {stub.get('title', '?')}")
                else:
                    total_errors += 1
                    print(f"  ! Fehler: {md_file.name}")

    # Speichern
    if total_errors and not args.allow_partial:
        data = original_data
        print("\nImport wegen Fehlern verworfen; JSON bleibt unverändert.")
    else:
        save_json(data, dry_run=args.dry_run)

    print(f"\n{'=' * 60}")
    print("  Ergebnis:")
    print(f"    Neu hinzugefügt: {total_added}")
    print(f"    Aktualisiert:     {total_updated}")
    print(f"    Fehler:           {total_errors}")
    print(f"    Gesamt:           {total_added + total_updated}")
    if not args.dry_run and (not total_errors or args.allow_partial):
        print(f"    Gespeichert in:   {JSON_PATH}")
    print("=" * 60)
    return 1 if total_errors else 0


if __name__ == "__main__":
    sys.exit(main())
