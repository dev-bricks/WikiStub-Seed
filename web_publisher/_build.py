"""Build-Schritt: Kopiert metawiki.json in web_publisher/data/ und erzeugt search-index.json."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SRC = ROOT / "metawiki.json"
OUT_DIR = Path(__file__).parent / "data"
OUT_DATA = OUT_DIR / "metawiki.json"
OUT_INDEX = OUT_DIR / "search-index.json"


def build():
    OUT_DIR.mkdir(exist_ok=True)
    raw = SRC.read_text(encoding="utf-8")
    data = json.loads(raw)

    # data/metawiki.json (exakte Kopie, kein Re-Encoding-Verlust)
    OUT_DATA.write_text(raw, encoding="utf-8")
    print(f"[build] {OUT_DATA} geschrieben")

    # Flacher Suchindex: Liste von {cat, sub, title, tags, id}
    wiki = data.get("MetaWiki", {})
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
                    "relevance": entry.get("relevance", ""),
                })
                entry_id += 1

    OUT_INDEX.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[build] {OUT_INDEX} geschrieben ({len(index)} Einträge)")


if __name__ == "__main__":
    build()
    print("[build] OK")
