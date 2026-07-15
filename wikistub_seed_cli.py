#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
wikistub_seed_cli.py - CLI-Tool für WikiStub-Seed Stub-Management
=========================================================

Einfaches Kommandozeilen-Interface für die wichtigsten Operationen:
- list:     Stubs auflisten (mit Filtern)
- search:   Stubs nach Titel/Inhalt suchen
- add:      Neuen Stub hinzufügen
- remove:   Stub entfernen
- stats:    Statistiken anzeigen
- export:   JSON nach Markdown exportieren
- import:   Markdown nach JSON importieren
- check:    Konsistenzprüfung

Nutzung:
    python wikistub_seed_cli.py list
    python wikistub_seed_cli.py search "Matrix"
    python wikistub_seed_cli.py add --title "Neues Thema" --definition "Beschreibung" --definition-en "Description" --relevance "Nutzen" --category 07_Informatik_KI --subcategory Software_Engineering
    python wikistub_seed_cli.py stats
"""

import sys
import argparse
from pathlib import Path
from collections import defaultdict

from language_model import (
    SUPPORTED_LANGUAGES,
    get_definition,
    get_relevance,
    identifier_key,
    normalize_entry,
)
from safe_io import (
    JsonDataError,
    atomic_write_json,
    atomic_write_text,
    backup_file,
    read_json_object,
    safe_path_component,
)

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


# ==================== HILFSFUNKTIONEN ====================

def load_json():
    """Lädt wikistub_seed.json."""
    data = read_json_object(JSON_PATH)
    root = data.get("MetaWiki")
    if not isinstance(root, dict):
        raise JsonDataError("wikistub_seed.json must contain an object at MetaWiki")
    for category, subcategories in root.items():
        if not isinstance(category, str) or not isinstance(subcategories, dict):
            raise JsonDataError("categories must be named JSON objects")
        for subcategory, entries in subcategories.items():
            if not isinstance(subcategory, str) or not isinstance(entries, list):
                raise JsonDataError(f"invalid subcategory structure at {category}")
            for entry in entries:
                if not isinstance(entry, dict) or not isinstance(entry.get("title"), str):
                    raise JsonDataError(f"invalid stub structure at {category}/{subcategory}")
                tags = entry.get("tags", [])
                if not isinstance(tags, list) or not all(
                    isinstance(tag, str) for tag in tags
                ):
                    raise JsonDataError(f"invalid tags at {category}/{subcategory}")
    return data


def load_json_or_report():
    """Load the authoritative dataset and report concise CLI errors."""
    try:
        return load_json()
    except JsonDataError as exc:
        print(f"\n  FEHLER: {exc}", file=sys.stderr)
        return None


def save_json(data):
    """Speichert wikistub_seed.json mit Backup."""
    if JSON_PATH.exists():
        backup_file(JSON_PATH, BACKUP_PATH, prefix="wikistub_seed", keep=10)

    atomic_write_json(JSON_PATH, data)


def get_all_stubs(data):
    """Gibt alle Stubs als flache Liste zurück."""
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
                annotated = dict(item)
                annotated["_category"] = cat
                annotated["_subcategory"] = subcat
                stubs.append(annotated)
    return stubs


# ==================== BEFEHLE ====================

def cmd_list(args):
    """Listet Stubs auf."""
    data = load_json_or_report()
    if data is None:
        return 1
    stubs = get_all_stubs(data)

    # Filter
    if args.category:
        stubs = [s for s in stubs if args.category.lower() in s["_category"].lower()]
    if args.subcategory:
        stubs = [s for s in stubs if args.subcategory.lower() in s["_subcategory"].lower()]

    # Sortieren
    stubs.sort(
        key=lambda stub: (
            str(stub["_category"]),
            str(stub["_subcategory"]),
            str(stub.get("title", "")),
        )
    )

    # Limit
    total = len(stubs)
    if args.limit is not None:
        if args.limit < 0:
            print("\n  FEHLER: --limit darf nicht negativ sein.", file=sys.stderr)
            return 2
        stubs = stubs[:args.limit]

    print(f"\n  {total} Stubs gefunden" + (f" (zeige {len(stubs)})" if args.limit else "") + "\n")

    current_cat = ""
    current_sub = ""
    for stub in stubs:
        if stub["_category"] != current_cat:
            current_cat = stub["_category"]
            cat_display = current_cat.lstrip("0123456789_").replace("_", " ")
            print(f"\n  [{cat_display}]")

        if stub["_subcategory"] != current_sub:
            current_sub = stub["_subcategory"]
            sub_display = current_sub.replace("_", " ")
            print(f"    {sub_display}:")

        print(f"      - {stub['title']}")
    return 0


def cmd_search(args):
    """Sucht in Stubs."""
    data = load_json_or_report()
    if data is None:
        return 1
    stubs = get_all_stubs(data)

    query = args.query.lower()
    results = []

    for stub in stubs:
        score = 0
        # Titel-Match (hoechste Prioritaet)
        title = stub.get("title", "") if isinstance(stub.get("title"), str) else ""
        if query in title.lower():
            score = 3
        # Definition-Match
        elif query in get_definition(stub, "de").lower() or query in get_definition(stub, "en").lower():
            score = 2
        # Relevanz-Match
        elif query in get_relevance(stub, "de").lower():
            score = 1
        # Tag-Match
        elif any(
            query in tag.lower()
            for tag in stub.get("tags", [])
            if isinstance(tag, str)
        ):
            score = 1

        if score > 0:
            results.append((stub, score))

    results.sort(key=lambda x: (-x[1], x[0]["title"]))

    print(f"\n  Suche: '{args.query}' -> {len(results)} Treffer\n")

    for stub, score in results:
        match_type = {3: "Titel", 2: "Definition", 1: "Relevanz/Tags"}[score]
        cat_display = stub["_category"].lstrip("0123456789_").replace("_", " ")
        sub_display = stub["_subcategory"].replace("_", " ")

        print(f"  [{match_type}] {stub['title']}")
        print(f"          {cat_display} > {sub_display}")
        definition = get_definition(stub, "de")
        if definition:
            defn = definition[:100]
            if len(definition) > 100:
                defn += "..."
            print(f"          {defn}")
        print()
    return 0


def cmd_add(args):
    """Fuegt einen neuen Stub hinzu."""
    data = load_json_or_report()
    if data is None:
        return 1

    cat = args.category
    subcat = args.subcategory

    # Validierung
    if cat not in data.get("MetaWiki", {}):
        if cat not in CATEGORY_FOLDERS:
            print(f"\n  FEHLER: Kategorie '{cat}' unbekannt.")
            print(f"  Verfügbar: {', '.join(CATEGORY_FOLDERS)}")
            return 2

    root = data["MetaWiki"]
    if cat not in root:
        root[cat] = {}
    elif not isinstance(root[cat], dict):
        print(f"\n  FEHLER: Kategorie '{cat}' hat eine ungültige Struktur.")
        return 1
    if subcat not in root[cat]:
        root[cat][subcat] = []
    elif not isinstance(root[cat][subcat], list):
        print(f"\n  FEHLER: Subkategorie '{cat}/{subcat}' ist keine Liste.")
        return 1

    # Duplikat pruefen
    for item in root[cat][subcat]:
        if not isinstance(item, dict):
            print(f"\n  FEHLER: Ungültiger Eintrag in {cat}/{subcat}.")
            return 1
        if identifier_key(item.get("title", "")) == identifier_key(args.title):
            print(f"\n  WARNUNG: '{args.title}' existiert bereits in {cat}/{subcat}.")
            return 2

    # Tags generieren
    tags = []
    tag_name = cat.lstrip("0123456789_").replace("_", " ")
    tags.append(tag_name)
    tags.append(subcat.replace("_", " "))

    stub = normalize_entry({
        "title": args.title,
        "definition_de": args.definition,
        "definition_en": args.definition_en,
        "relevance": args.relevance,
        "tags": tags
    })

    root[cat][subcat].append(stub)
    save_json(data)
    print(f"\n  Hinzugefügt: '{args.title}' -> {cat}/{subcat}")
    return 0


def cmd_remove(args):
    """Entfernt einen Stub."""
    data = load_json_or_report()
    if data is None:
        return 1
    query = args.title.lower()

    found = []
    for cat, subcats in data.get("MetaWiki", {}).items():
        if not isinstance(subcats, dict):
            continue
        for subcat, items in subcats.items():
            if not isinstance(items, list):
                continue
            for i, item in enumerate(items):
                if not isinstance(item, dict):
                    continue
                title_value = item.get("title", "")
                if isinstance(title_value, str) and title_value.lower() == query:
                    found.append((cat, subcat, i, str(item.get("title", ""))))

    if not found:
        print(f"\n  Kein Stub mit Titel '{args.title}' gefunden.")
        return 2

    if len(found) > 1:
        print(f"\n  Mehrere Treffer für '{args.title}':")
        for idx, (cat, subcat, _, title) in enumerate(found):
            print(f"    {idx+1}. {title} in {cat}/{subcat}")
        print("\n  Bitte genauer spezifizieren.")
        return 2

    cat, subcat, idx, title = found[0]
    del data["MetaWiki"][cat][subcat][idx]
    save_json(data)
    print(f"\n  Entfernt: '{title}' aus {cat}/{subcat}")
    return 0


def cmd_stats(args):
    """Zeigt Statistiken."""
    data = load_json_or_report()
    if data is None:
        return 1
    stubs = get_all_stubs(data)

    cat_counts = defaultdict(int)
    sub_counts = defaultdict(lambda: defaultdict(int))
    tag_counts = defaultdict(int)
    empty_def = 0
    empty_rel = 0

    for stub in stubs:
        cat_counts[stub["_category"]] += 1
        sub_counts[stub["_category"]][stub["_subcategory"]] += 1
        for tag in stub.get("tags", []):
            if isinstance(tag, str):
                tag_counts[tag] += 1
        if not get_definition(stub, "de").strip():
            empty_def += 1
        if not get_relevance(stub, "de").strip():
            empty_rel += 1

    print(f"\n  {'='*50}")
    print("  WikiStub-Seed Statistiken")
    print(f"  {'='*50}")
    print(f"\n  Gesamt: {len(stubs)} Stubs")
    print(f"  Kategorien: {len(cat_counts)}")
    print(f"  Subkategorien: {sum(len(s) for s in sub_counts.values())}")
    print(f"  Ohne Definition: {empty_def}")
    print(f"  Ohne Relevanz: {empty_rel}")

    print("\n  Verteilung:")
    for cat in sorted(cat_counts.keys()):
        cat_display = cat.lstrip("0123456789_").replace("_", " ")
        bar = "#" * (cat_counts[cat] // 2)
        print(f"    {cat_display:35s} {cat_counts[cat]:4d} {bar}")

        if args.verbose:
            for subcat in sorted(sub_counts[cat].keys()):
                sub_display = subcat.replace("_", " ")
                print(f"      {sub_display:33s} {sub_counts[cat][subcat]:4d}")

    print("\n  Top 10 Tags:")
    for tag, count in sorted(tag_counts.items(), key=lambda x: -x[1])[:10]:
        print(f"    {tag:30s} {count:4d}")
    return 0


def cmd_export(args):
    """Exportiert JSON nach Markdown."""
    data = load_json_or_report()
    if data is None:
        return 1
    stubs = get_all_stubs(data)
    output_dir = BASE_PATH / "output"
    exported = 0
    failures = 0
    destinations = set()
    language = getattr(args, "lang", "de")

    for stub in stubs:
        cat = stub["_category"]
        subcat = stub["_subcategory"]
        folder = output_dir / safe_path_component(cat) / safe_path_component(subcat)
        folder.mkdir(parents=True, exist_ok=True)

        safe_title = safe_path_component(stub["title"].replace(" ", "_"))
        filepath = folder / f"{safe_title}.md"
        resolved = filepath.resolve()
        if resolved in destinations:
            print(f"  FEHLER: Exportziel kollidiert: {filepath}", file=sys.stderr)
            failures += 1
            continue
        destinations.add(resolved)

        cat_display = cat.lstrip("0123456789_").replace("_", " ")
        sub_display = subcat.replace("_", " ")

        content = f"# {stub['title']}\n\n"
        label = "Kurzdefinition" if language == "de" else f"Definition ({language.upper()})"
        relevance_label = (
            "Relevanz" if language == "de" else f"Relevanz ({language.upper()})"
        )
        content += f"**{label}:**\n{get_definition(stub, language)}\n\n"
        content += f"**Kategorie:**\n{cat_display} > {sub_display}\n\n"
        content += f"**{relevance_label}:**\n{get_relevance(stub, language)}\n\n"
        if language != "de":
            content += f"**Definition (DE):**\n{get_definition(stub, 'de')}\n\n"
            content += f"**Relevanz (DE):**\n{get_relevance(stub, 'de')}\n\n"
        if stub.get("tags"):
            content += f"**Tags:**\n{', '.join(stub['tags'])}\n"

        try:
            atomic_write_text(filepath, content)
            exported += 1
        except OSError as exc:
            print(f"  FEHLER beim Schreiben von {filepath}: {exc}", file=sys.stderr)
            failures += 1

    print(f"\n  {exported} Stubs exportiert nach {output_dir}")
    return 1 if failures else 0


def cmd_import_md(args):
    """Importiert Markdown-Dateien."""
    # Delegiere an md_to_json.py
    import subprocess
    cmd = [sys.executable, str(BASE_PATH / "md_to_json.py")]
    if args.dry_run:
        cmd.append("--dry-run")
    try:
        return subprocess.run(cmd, timeout=180, check=False).returncode
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(f"FEHLER: Import-Unterprozess fehlgeschlagen: {exc}", file=sys.stderr)
        return 1


def cmd_check(args):
    """Konsistenzprüfung."""
    # Delegiere an check_duplicates.py
    import subprocess
    cmd = [sys.executable, str(BASE_PATH / "check_duplicates.py")]
    if args.similar:
        cmd.append("--similar")
    try:
        return subprocess.run(cmd, timeout=180, check=False).returncode
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(f"FEHLER: Check-Unterprozess fehlgeschlagen: {exc}", file=sys.stderr)
        return 1


# ==================== MAIN ====================

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="WikiStub-Seed CLI - Stub-Management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  wikistub_seed_cli.py list                                    # Alle Stubs auflisten
  wikistub_seed_cli.py list --category 07 --limit 20           # Informatik, max 20
  wikistub_seed_cli.py search "Matrix"                         # Suche nach "Matrix"
  wikistub_seed_cli.py add -t "Neues Thema" -d "Definition" --definition-en "Definition"
                  -r "Relevanz" -c 07_Informatik_KI -s Software_Engineering
  wikistub_seed_cli.py remove -t "Altes Thema"                 # Stub entfernen
  wikistub_seed_cli.py stats                                   # Statistiken
  wikistub_seed_cli.py stats -v                                # Detaillierte Statistiken
  wikistub_seed_cli.py export                                  # JSON -> Markdown
  wikistub_seed_cli.py import                                  # Markdown -> JSON
  wikistub_seed_cli.py check --similar                         # Konsistenzprüfung
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Verfügbare Befehle")

    # list
    p_list = subparsers.add_parser("list", help="Stubs auflisten")
    p_list.add_argument("--category", "-c", help="Nach Kategorie filtern")
    p_list.add_argument("--subcategory", "-s", help="Nach Subkategorie filtern")
    p_list.add_argument("--limit", "-l", type=int, help="Maximale Anzahl")
    p_list.set_defaults(func=cmd_list)

    # search
    p_search = subparsers.add_parser("search", help="Stubs suchen")
    p_search.add_argument("query", help="Suchbegriff")
    p_search.set_defaults(func=cmd_search)

    # add
    p_add = subparsers.add_parser("add", help="Stub hinzufuegen")
    p_add.add_argument("--title", "-t", required=True, help="Titel des Stubs")
    p_add.add_argument("--definition", "-d", required=True, help="Definition (DE)")
    p_add.add_argument(
        "--definition-en",
        required=True,
        help="Definition (EN)",
    )
    p_add.add_argument("--relevance", "-r", required=True, help="Relevanz (DE)")
    p_add.add_argument("--category", "-c", required=True, help="Kategorie (z.B. 07_Informatik_KI)")
    p_add.add_argument("--subcategory", "-s", required=True, help="Subkategorie (z.B. Software_Engineering)")
    p_add.set_defaults(func=cmd_add)

    # remove
    p_remove = subparsers.add_parser("remove", help="Stub entfernen")
    p_remove.add_argument("--title", "-t", required=True, help="Titel des Stubs")
    p_remove.set_defaults(func=cmd_remove)

    # stats
    p_stats = subparsers.add_parser("stats", help="Statistiken anzeigen")
    p_stats.add_argument("--verbose", "-v", action="store_true", help="Detaillierte Ausgabe")
    p_stats.set_defaults(func=cmd_stats)

    # export
    p_export = subparsers.add_parser("export", help="JSON nach Markdown exportieren")
    p_export.add_argument(
        "--lang",
        choices=SUPPORTED_LANGUAGES,
        default="de",
        help="Ausgabesprache mit Fallback (default: de)",
    )
    p_export.set_defaults(func=cmd_export)

    # import
    p_import = subparsers.add_parser("import", help="Markdown nach JSON importieren")
    p_import.add_argument("--dry-run", action="store_true", help="Nur anzeigen")
    p_import.set_defaults(func=cmd_import_md)

    # check
    p_check = subparsers.add_parser("check", help="Konsistenzprüfung")
    p_check.add_argument("--similar", action="store_true", help="Ähnliche Titel finden")
    p_check.set_defaults(func=cmd_check)

    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    exit_code = args.func(args)
    return exit_code if isinstance(exit_code, int) else 0


if __name__ == "__main__":
    sys.exit(main())
