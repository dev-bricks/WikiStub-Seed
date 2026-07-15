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

import json
import re
import sys
from pathlib import Path
from datetime import datetime

from language_model import (
    existing_mapping_key,
    identifier_key,
    merge_entry,
    normalize_entry,
    public_entry,
)
from safe_io import atomic_write_json, backup_file

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
    relevance = ""
    category_text = ""

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
                elif current_section == "kategorie":
                    category_text = text
                elif current_section == "relevanz":
                    relevance = text

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
            elif header == "kategorie" and inline_text:
                category_text = inline_text
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

        # Inhalt sammeln
        if current_section and stripped:
            section_lines.append(stripped)

    # Letzte Sektion
    if current_section and section_lines:
        text = ' '.join(section_lines).strip()
        if current_section == "kurzdefinition":
            definition = text
        elif current_section == "kategorie":
            category_text = text
        elif current_section == "relevanz":
            relevance = text

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
    tags = []
    if cat:
        tag_name = cat.lstrip("0123456789_").replace("_", " ")
        tags.append(tag_name)
    if subcat:
        tags.append(subcat.replace("_", " "))

    return normalize_entry({
        "title": title,
        "definition_de": definition,
        "definition_en": "",
        "relevance": relevance,
        "tags": tags,
        "_category": cat,
        "_subcategory": subcat
    })


def load_json():
    """Laedt die bestehende wikistub_seed.json oder erstellt Grundstruktur."""
    if JSON_PATH.exists():
        try:
            with open(JSON_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"FEHLER beim Lesen der JSON: {e}")
            sys.exit(1)

    # Grundstruktur erstellen
    data = {"MetaWiki": {}}
    for cat in CATEGORY_FOLDERS:
        data["MetaWiki"][cat] = {}
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

    root = data["MetaWiki"]
    category = existing_mapping_key(root, cat)
    if category not in root:
        root[category] = {}
    subcategory = existing_mapping_key(root[category], subcat)
    if subcategory not in root[category]:
        root[category][subcategory] = []

    # Duplikat-Pruefung innerhalb der gleichen Subkategorie
    existing = root[category][subcategory]
    for i, item in enumerate(existing):
        if identifier_key(item.get("title", "")) == identifier_key(incoming["title"]):
            existing[i] = merge_entry(item, incoming)
            return "updated"

    existing.append(public_entry(incoming))
    return "added"


def main():
    import argparse
    parser = argparse.ArgumentParser(description="WikiStub-Seed: Markdown zu JSON Konverter")
    parser.add_argument("--dry-run", action="store_true", help="Nur anzeigen, nicht speichern")
    parser.add_argument("--category", type=str, help="Nur bestimmte Kategorie (z.B. '07')")
    args = parser.parse_args()

    print("=" * 60)
    print("  WikiStub-Seed: Markdown -> JSON Konverter")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    data = load_json()

    # Kategorien filtern
    categories = CATEGORY_FOLDERS
    if args.category:
        categories = [c for c in categories if c.startswith(args.category)]
        if not categories:
            print(f"Keine Kategorie mit Prefix '{args.category}' gefunden.")
            return

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
                    result = add_stub_to_data(data, stub)
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
    save_json(data, dry_run=args.dry_run)

    print(f"\n{'=' * 60}")
    print(f"  Ergebnis:")
    print(f"    Neu hinzugefügt: {total_added}")
    print(f"    Aktualisiert:     {total_updated}")
    print(f"    Fehler:           {total_errors}")
    print(f"    Gesamt:           {total_added + total_updated}")
    if not args.dry_run:
        print(f"    Gespeichert in:   {JSON_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    main()
