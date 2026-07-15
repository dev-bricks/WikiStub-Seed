#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_duplicates.py - Konsistenzprüfung für WikiStub-Seed
======================================================

Prueft wikistub_seed.json auf:
- Duplikate: Gleiche Titel in verschiedenen Kategorien/Subkategorien
- Ähnliche Titel: Levenshtein-Distanz-basierte Erkennung
- Leere Einträge: Stubs ohne Definition oder Relevanz

Nutzung:
    python check_duplicates.py                # Standard-Pruefung
    python check_duplicates.py --similar      # Auch aehnliche Titel finden
    python check_duplicates.py --fix          # Interaktiv bereinigen
"""

import math
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime

from language_model import get_definition, get_relevance, identifier_key
from data_policy import duplicate_locations_are_allowed
from safe_io import JsonDataError, atomic_write_json, backup_file, read_json_object

BASE_PATH = Path(__file__).parent.resolve()
JSON_PATH = BASE_PATH / "wikistub_seed.json"
BACKUP_PATH = BASE_PATH / "backups"


def load_json():
    """Laedt wikistub_seed.json."""
    try:
        data = read_json_object(JSON_PATH)
    except JsonDataError as exc:
        print(f"FEHLER: {exc}")
        return None
    root = data.get("MetaWiki")
    if not isinstance(root, dict):
        print("FEHLER: MetaWiki muss ein Objekt sein.")
        return None
    for category, subcategories in root.items():
        if not isinstance(category, str) or not isinstance(subcategories, dict):
            print("FEHLER: Kategorien müssen benannte Objekte sein.")
            return None
        for subcategory, entries in subcategories.items():
            if not isinstance(subcategory, str) or not isinstance(entries, list):
                print(f"FEHLER: Ungültige Subkategorie in {category}.")
                return None
            if any(not isinstance(entry, dict) for entry in entries):
                print(f"FEHLER: Ungültiger Stub in {category}/{subcategory}.")
                return None
    return data


def get_all_stubs(data):
    """Extrahiert alle Stubs mit Kategorie-Info."""
    stubs = []
    for cat, subcats in data.get("MetaWiki", {}).items():
        if not isinstance(subcats, dict):
            continue
        for subcat, items in subcats.items():
            if not isinstance(items, list):
                continue
            for item in items:
                if not isinstance(item, dict):
                    continue
                stubs.append({
                    "title": item.get("title", "") if isinstance(item.get("title"), str) else "",
                    "definition_de": get_definition(item, "de"),
                    "relevance": get_relevance(item, "de"),
                    "tags": item.get("tags", []) if isinstance(item.get("tags"), list) else [],
                    "category": cat,
                    "subcategory": subcat
                })
    return stubs


def find_exact_duplicates(stubs):
    """Findet exakte Titel-Duplikate (case-insensitive)."""
    title_map = defaultdict(list)
    for stub in stubs:
        key = identifier_key(stub["title"])
        title_map[key].append(stub)

    duplicates = {k: v for k, v in title_map.items() if len(v) > 1}
    return duplicates


def find_similar_titles(stubs, threshold=0.85):
    """Findet ähnliche Titel mittels einfacher Ähnlichkeitsmessung."""
    similar = []
    titles = [(s["title"], s) for s in stubs if isinstance(s["title"], str)]

    for i in range(len(titles)):
        for j in range(i + 1, len(titles)):
            t1, s1 = titles[i]
            t2, s2 = titles[j]

            # Gleiche Kategorie + Subkategorie -> kein interessanter Fund
            if s1["category"] == s2["category"] and s1["subcategory"] == s2["subcategory"]:
                continue

            ratio = _similarity(t1.lower(), t2.lower())
            if ratio >= threshold and t1.lower() != t2.lower():
                similar.append((s1, s2, ratio))

    return sorted(similar, key=lambda x: -x[2])


def _similarity(a, b):
    """Einfache Zeichenkettenaehnlichkeit (SequenceMatcher-Algorithmus)."""
    from difflib import SequenceMatcher
    return SequenceMatcher(None, a, b).ratio()


def save_json(data):
    """Speichert wikistub_seed.json mit Backup."""
    if JSON_PATH.exists():
        backup_file(JSON_PATH, BACKUP_PATH, prefix="wikistub_seed", keep=10)

    atomic_write_json(JSON_PATH, data)


def fix_duplicates_interactive(data, duplicates):
    """
    Loest exakte Duplikate interaktiv auf.
    Der Nutzer wählt für jedes Duplikat-Set, welcher Eintrag behalten werden soll.
    """
    removed = 0

    for title_key, entries in sorted(duplicates.items()):
        print(f"\n  Duplikat: '{entries[0]['title']}'")
        for i, e in enumerate(entries):
            print(f"    [{i + 1}] {e['category']}/{e['subcategory']}")
            if e.get("definition_de"):
                preview = e["definition_de"][:80]
                if len(e["definition_de"]) > 80:
                    preview += "..."
                print(f"        {preview}")

        print("    [s] Ueberspringen")

        while True:
            try:
                choice = input(f"  Welchen Eintrag behalten? [1-{len(entries)}/s]: ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\n  Abgebrochen.")
                return removed

            if choice == "s":
                break

            try:
                idx = int(choice) - 1
                if 0 <= idx < len(entries):
                    keep = entries[idx]
                    kept_selected = False
                    for category, subcategories in data["MetaWiki"].items():
                        for subcategory, items in subcategories.items():
                            retained = []
                            for item in items:
                                if identifier_key(item.get("title", "")) != title_key:
                                    retained.append(item)
                                elif (
                                    not kept_selected
                                    and category == keep["category"]
                                    and subcategory == keep["subcategory"]
                                ):
                                    retained.append(item)
                                    kept_selected = True
                                else:
                                    removed += 1
                            data["MetaWiki"][category][subcategory] = retained

                    print(f"  Behalten: {keep['category']}/{keep['subcategory']}")
                    break
            except ValueError:
                pass

            print(f"  Ungültige Eingabe. Bitte 1-{len(entries)} oder 's'.")

    return removed


def find_empty_entries(stubs):
    """Findet Stubs mit fehlenden Pflichtfeldern."""
    empty = []
    for stub in stubs:
        issues = []
        if not stub["definition_de"].strip():
            issues.append("definition_de leer")
        if not stub["relevance"].strip():
            issues.append("relevanz leer")
        if not stub["tags"]:
            issues.append("keine tags")
        if issues:
            empty.append((stub, issues))
    return empty


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description="WikiStub-Seed: Konsistenzprüfung")
    parser.add_argument("--similar", action="store_true", help="Auch ähnliche Titel finden")
    parser.add_argument("--threshold", type=float, default=0.85, help="Ähnlichkeits-Schwellwert (0-1)")
    parser.add_argument("--fix", action="store_true", help="Exakte Duplikate interaktiv bereinigen")
    args = parser.parse_args(argv)

    if not math.isfinite(args.threshold) or not 0 <= args.threshold <= 1:
        parser.error("--threshold muss eine endliche Zahl zwischen 0 und 1 sein")

    print("=" * 60)
    print("  WikiStub-Seed: Konsistenzprüfung")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    data = load_json()
    if data is None:
        return 1
    stubs = get_all_stubs(data)
    print(f"\nGeprüft: {len(stubs)} Stubs")

    # 1. Exakte Duplikate
    print(f"\n{'='*60}")
    print("  1. EXAKTE DUPLIKATE (gleicher Titel)")
    print(f"{'='*60}")

    duplicates = find_exact_duplicates(stubs)
    allowed_duplicates = {
        title: entries
        for title, entries in duplicates.items()
        if duplicate_locations_are_allowed(
            title,
            ((entry["category"], entry["subcategory"]) for entry in entries),
        )
    }
    unexpected_duplicates = {
        title: entries for title, entries in duplicates.items() if title not in allowed_duplicates
    }
    if duplicates:
        print(f"\n  {len(duplicates)} Duplikate gefunden:\n")
        for title, entries in sorted(duplicates.items()):
            print(f"  [{title}]")
            for e in entries:
                print(f"    -> {e['category']}/{e['subcategory']}")
            print()

        if allowed_duplicates:
            print(
                f"  {len(allowed_duplicates)} geprüfte domänenübergreifende "
                "Doppelbezeichnung(en) sind erlaubt."
            )
        if unexpected_duplicates:
            print(f"  FEHLER: {len(unexpected_duplicates)} unerwartete Duplikatgruppe(n).")

        if args.fix and unexpected_duplicates:
            print(f"\n{'='*60}")
            print("  INTERAKTIVE BEREINIGUNG")
            print(f"{'='*60}")
            removed = fix_duplicates_interactive(data, unexpected_duplicates)
            if removed > 0:
                save_json(data)
                print(f"\n  {removed} Duplikate entfernt und gespeichert.")
            else:
                print("\n  Keine Änderungen vorgenommen.")
    else:
        print("\n  Keine exakten Duplikate gefunden.")

    # 2. Ähnliche Titel
    if args.similar:
        print(f"\n{'='*60}")
        print(f"  2. ÄHNLICHE TITEL (Schwellwert: {args.threshold})")
        print(f"{'='*60}")

        similar = find_similar_titles(stubs, args.threshold)
        if similar:
            print(f"\n  {len(similar)} ähnliche Paare gefunden:\n")
            for s1, s2, ratio in similar[:30]:  # Max 30 anzeigen
                print(f"  [{ratio:.0%}] '{s1['title']}' <-> '{s2['title']}'")
                print(f"         {s1['category']}/{s1['subcategory']}")
                print(f"         {s2['category']}/{s2['subcategory']}")
                print()
        else:
            print("\n  Keine ähnlichen Titel gefunden.")

    # 3. Leere Einträge
    print(f"\n{'='*60}")
    print("  3. UNVOLLSTÄNDIGE EINTRÄGE")
    print(f"{'='*60}")

    empty = find_empty_entries(stubs)
    if empty:
        print(f"\n  {len(empty)} unvollständige Einträge:\n")
        for stub, issues in empty[:50]:  # Max 50 anzeigen
            print(f"  [{stub['category']}/{stub['subcategory']}] {stub['title']}")
            for issue in issues:
                print(f"    - {issue}")
    else:
        print("\n  Alle Einträge vollständig.")

    # Zusammenfassung
    print(f"\n{'='*60}")
    print("  ZUSAMMENFASSUNG")
    print(f"{'='*60}")
    print(f"    Gesamt Stubs:         {len(stubs)}")
    print(f"    Exakte Duplikate:     {len(duplicates)}")
    print(f"    Davon erlaubt:        {len(allowed_duplicates)}")
    if args.similar:
        print(f"    Ähnliche Titel:       {len(similar)}")
    print(f"    Unvollständige:       {len(empty)}")
    print(f"{'='*60}")

    return 1 if unexpected_duplicates or empty else 0


if __name__ == "__main__":
    sys.exit(main())
