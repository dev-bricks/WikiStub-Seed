"""Build-Schritt: Kopiert metawiki.json in web_publisher/data/ und erzeugt search-index.json."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from language_model import get_definition, get_relevance, normalize_metawiki_data

SRC = ROOT / "metawiki.json"
OUT_DIR = Path(__file__).parent / "data"
OUT_DATA = OUT_DIR / "metawiki.json"
OUT_INDEX = OUT_DIR / "search-index.json"


def build():
    OUT_DIR.mkdir(exist_ok=True)
    data = json.loads(SRC.read_text(encoding="utf-8"))
    normalized_data = normalize_metawiki_data(data)

    # data/metawiki.json bleibt aus metawiki.json abgeleitet, enthält aber normalisierte Sprachmaps.
    OUT_DATA.write_text(
        json.dumps(normalized_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"[build] {OUT_DATA} geschrieben")

    # Flacher Suchindex: Liste von {cat, sub, title, tags, id}
    wiki = normalized_data.get("MetaWiki", {})
    index = []
    entry_id = 0
    for cat, subs in wiki.items():
        for sub, entries in subs.items():
            for entry in entries:
                index.append({
                    "id": entry_id,
                    "cat": cat,
                    "sub": sub,
                    "title": entry.get("title", ""),
                    "tags": entry.get("tags", []),
                    "definitions": entry.get("definitions", {}),
                    "relevance_i18n": entry.get("relevance_i18n", {}),
                    "definition_de": get_definition(entry, "de"),
                    "definition_en": get_definition(entry, "en"),
                    "relevance": get_relevance(entry, "de"),
                })
                entry_id += 1

    OUT_INDEX.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[build] {OUT_INDEX} geschrieben ({len(index)} Einträge)")


if __name__ == "__main__":
    build()
    print("[build] OK")
