import json
import os
import argparse
import sys
from pathlib import Path

from language_model import get_definition, get_relevance, normalize_entry
from safe_io import atomic_write_text, safe_path_component

try:
    from translate import estimate_batch_max_cost_usd, translate_text as _translate_api
    _API_AVAILABLE = True
except ImportError:
    _API_AVAILABLE = False


def translate(text, target_lang="en"):
    """
    Uebersetzt Text via Claude API (translate.py).
    Erfordert: pip install anthropic && ANTHROPIC_API_KEY gesetzt.
    Gibt leeren String zurück falls API nicht verfügbar.
    """
    if not text:
        return ""
    if _API_AVAILABLE:
        return _translate_api(text, target_lang)
    return ""

def main(argv=None):
    parser = argparse.ArgumentParser(description="Legacy WikiStub-Seed Markdown export")
    parser.add_argument(
        "--translate-missing",
        action="store_true",
        help="Fehlende EN-Texte über die optionale externe API ergänzen",
    )
    parser.add_argument(
        "--max-translations",
        type=int,
        default=0,
        help="Explizite Obergrenze kostenpflichtiger API-Aufrufe",
    )
    parser.add_argument(
        "--confirm-api-cost",
        action="store_true",
        help="Bestätigt ausdrücklich mögliche API-Kosten",
    )
    parser.add_argument(
        "--max-budget-usd",
        type=float,
        default=0,
        help="Explizite konservative Kostenobergrenze in USD",
    )
    args = parser.parse_args(argv)
    if args.translate_missing and (
        args.max_translations <= 0
        or args.max_budget_usd <= 0
        or not args.confirm_api_cost
    ):
        parser.error(
            "--translate-missing benötigt --max-translations > 0, "
            "--max-budget-usd > 0 und --confirm-api-cost"
        )

    print("Starte WikiStub-Seed Pipeline...")
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_path, "wikistub_seed.json")
    
    if not os.path.exists(json_path):
        print(f"FEHLER: {json_path} nicht gefunden.")
        return 1

    # JSON laden
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"FEHLER beim Lesen von {json_path}: {e}")
        return 1

    # Verarbeitung
    root_key = "MetaWiki"
    if root_key not in data:
        print(f"FEHLER: Root-Key '{root_key}' fehlt in JSON.")
        return 1

    if args.translate_missing:
        candidates = []
        for subcats in data[root_key].values():
            for stubs in subcats.values():
                for stub in stubs:
                    normalized = normalize_entry(stub)
                    if not get_definition(normalized, "en"):
                        candidates.append(get_definition(normalized, "de"))
                        if len(candidates) >= args.max_translations:
                            break
                if len(candidates) >= args.max_translations:
                    break
            if len(candidates) >= args.max_translations:
                break
        projected_cost = estimate_batch_max_cost_usd(candidates)
        if projected_cost > args.max_budget_usd:
            print(
                f"FEHLER: Maximale Laufkosten ${projected_cost:.6f} überschreiten "
                f"Budget ${args.max_budget_usd:.6f}."
            )
            return 1

    count_processed = 0
    translation_calls = 0
    failures = 0
    
    for category, subcats in data[root_key].items():
        print(f"Verarbeite Kategorie: {category}")
        for subcat, stubs in subcats.items():
            for stub in stubs:
                title = stub.get("title", "Unbenannt")
                print(f"  - Generiere Stub: {title}")
                
                # Auto-Übersetzung (Simulation)
                stub.update(normalize_entry(stub))
                if (
                    not get_definition(stub, "en")
                    and args.translate_missing
                    and translation_calls < args.max_translations
                ):
                    translated = translate(get_definition(stub, "de"))
                    translation_calls += 1
                    stub["definition_en"] = translated
                    stub.setdefault("definitions", {})["en"] = translated

                # Tags verarbeiten
                tags_list = stub.get("tags", [])
                tags_str = ', '.join(tags_list)

                # Ordnerstruktur
                # HINWEIS: Wir nutzen hier 'output' als Basis, um nichts zu ueberschreiben.
                # Spaeter kann dies auf '.' geaendet werden.
                folder = (
                    Path(base_path)
                    / "output"
                    / safe_path_component(category)
                    / safe_path_component(subcat)
                )
                folder.mkdir(parents=True, exist_ok=True)

                # Markdown generieren
                safe_title = safe_path_component(title.replace(" ", "_"))
                filename = folder / f"{safe_title}.md"
                
                try:
                    content = (
                        f"# {title}\n\n"
                        f"**Definition (DE):** {get_definition(stub, 'de')}\n\n"
                        f"**Definition (EN):** {get_definition(stub, 'en')}\n\n"
                        f"**Relevanz:** {get_relevance(stub, 'de')}\n\n"
                        f"**Tags:** {tags_str}\n"
                    )
                    atomic_write_text(filename, content)
                    
                    count_processed += 1
                except IOError as e:
                    print(f"    FEHLER beim Schreiben von {filename}: {e}")
                    failures += 1

    print(f"\nFertig! {count_processed} Stubs generiert.")
    return 1 if failures else 0

if __name__ == "__main__":
    sys.exit(main())
