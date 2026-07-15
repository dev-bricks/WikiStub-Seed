"""Erzeuge validierte, reproduzierbare PWA-Daten aus der kanonischen JSON-Datei."""
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from language_model import get_definition, get_relevance, normalize_metawiki_data  # noqa: E402
from safe_io import atomic_write_json, read_json_object  # noqa: E402

SRC = ROOT / "wikistub_seed.json"
OUT_DIR = Path(__file__).parent / "data"
OUT_DATA = OUT_DIR / "wikistub_seed.json"
OUT_INDEX = OUT_DIR / "search-index.json"


def build():
    OUT_DIR.mkdir(exist_ok=True)
    data = read_json_object(SRC)
    if not isinstance(data.get("MetaWiki"), dict):
        raise ValueError("MetaWiki muss ein Objekt sein")
    normalized_data = normalize_metawiki_data(data)

    # Flacher Suchindex: Liste von {cat, sub, title, tags, id}
    wiki = normalized_data.get("MetaWiki", {})
    index = []
    seen_ids = set()
    for cat, subs in wiki.items():
        if not isinstance(cat, str) or not isinstance(subs, dict):
            raise ValueError(f"Ungültige Kategorie: {cat!r}")
        for sub, entries in subs.items():
            if not isinstance(sub, str) or not isinstance(entries, list):
                raise ValueError(f"Ungültige Subkategorie: {cat}/{sub}")
            for entry in entries:
                if not isinstance(entry, dict) or not isinstance(entry.get("title"), str):
                    raise ValueError(f"Ungültiger Eintrag in {cat}/{sub}")
                identity = "\0".join((cat, sub, entry["title"])).encode("utf-8")
                entry_id = hashlib.sha256(identity).hexdigest()[:20]
                if entry_id in seen_ids:
                    raise ValueError(f"Doppelte stabile ID für {cat}/{sub}/{entry['title']}")
                seen_ids.add(entry_id)
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

    # Erst nach vollständiger Validierung schreiben, damit fehlerhafte Quellen
    # kein neues Datenfile neben einem alten Suchindex hinterlassen.
    atomic_write_json(OUT_DATA, normalized_data)
    print(f"[build] {OUT_DATA} geschrieben")
    atomic_write_json(OUT_INDEX, index)
    print(f"[build] {OUT_INDEX} geschrieben ({len(index)} Einträge)")
    return len(index)


if __name__ == "__main__":
    build()
    print("[build] OK")
