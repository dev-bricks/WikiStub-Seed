import json
import os

from language_model import get_definition, get_relevance, normalize_entry

try:
    from translate import translate_text as _translate_api
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

def main():
    print("Starte WikiStub-Seed Pipeline...")
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_path, "wikistub_seed.json")
    
    if not os.path.exists(json_path):
        print(f"FEHLER: {json_path} nicht gefunden.")
        return

    # JSON laden
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"FEHLER beim Lesen von {json_path}: {e}")
        return

    # Verarbeitung
    root_key = "MetaWiki"
    if root_key not in data:
        print(f"FEHLER: Root-Key '{root_key}' fehlt in JSON.")
        return

    count_processed = 0
    
    for category, subcats in data[root_key].items():
        print(f"Verarbeite Kategorie: {category}")
        for subcat, stubs in subcats.items():
            for stub in stubs:
                title = stub.get("title", "Unbenannt")
                print(f"  - Generiere Stub: {title}")
                
                # Auto-Übersetzung (Simulation)
                stub.update(normalize_entry(stub))
                if not get_definition(stub, "en"):
                    translated = translate(get_definition(stub, "de"))
                    stub["definition_en"] = translated
                    stub.setdefault("definitions", {})["en"] = translated

                # Tags verarbeiten
                tags_list = stub.get("tags", [])
                tags_str = ', '.join(tags_list)

                # Ordnerstruktur
                # HINWEIS: Wir nutzen hier 'output' als Basis, um nichts zu ueberschreiben.
                # Spaeter kann dies auf '.' geaendet werden.
                folder = os.path.join(base_path, "output", category, subcat)
                os.makedirs(folder, exist_ok=True)

                # Markdown generieren
                safe_title = title.replace(' ', '_')
                filename = f"{folder}/{safe_title}.md"
                
                try:
                    with open(filename, "w", encoding="utf-8") as md:
                        md.write(f"# {title}\n\n")
                        md.write(f"**Definition (DE):** {get_definition(stub, 'de')}\n\n")
                        md.write(f"**Definition (EN):** {get_definition(stub, 'en')}\n\n")
                        md.write(f"**Relevanz:** {get_relevance(stub, 'de')}\n\n")
                        md.write(f"**Tags:** {tags_str}\n")
                    
                    count_processed += 1
                except IOError as e:
                    print(f"    FEHLER beim Schreiben von {filename}: {e}")

    print(f"\nFertig! {count_processed} Stubs generiert.")

if __name__ == "__main__":
    main()
