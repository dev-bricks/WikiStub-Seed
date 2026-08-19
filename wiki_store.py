"""Pure CRUD + trash operations on wikistub_seed.json (T-20260819-782505468).

Exists alongside wikistub_seed_cli.py's cmd_add/cmd_remove rather than
replacing them: the CLI's inline functions are narrow, single-purpose,
argparse- and print()-bound, and already covered by their own green tests --
touching them risks that coverage for no benefit. This module is the
general-purpose, non-CLI surface edit_server.py (the GUI editor) needs:
every function here takes and returns plain dicts/paths, so it is usable
from an HTTP handler (or a future refactored CLI) without duplicating the
mutation logic in either place.

Categories/subcategories are NOT restricted to wikistub_seed_cli.CATEGORY_FOLDERS
here on purpose -- that fixed list is the pre-existing taxonomy; this ticket's
whole point is letting the GUI create new categories/subcategories, so a hard
allowlist would defeat the feature. New names are still validated (see
_validate_component_name) so they can never produce a path-traversal-shaped
string, matching safe_path_component's existing guarantees elsewhere in this
project (used by cmd_export already).

Soft delete only: nothing here ever drops data on the floor. delete_entry/
delete_category/delete_subcategory move their payload into a trash file
(wikistub_seed_trash.json, gitignored, instance-local) instead of discarding
it, and restore_entry_from_trash is the documented inverse.
"""
from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from language_model import existing_mapping_key, identifier_key, merge_entry, normalize_entry
from safe_io import atomic_write_json, backup_file, read_json_object, safe_path_component

BASE_PATH = Path(__file__).parent.resolve()
JSON_PATH = BASE_PATH / "wikistub_seed.json"
BACKUP_PATH = BASE_PATH / "backups"
TRASH_PATH = BASE_PATH / "wikistub_seed_trash.json"

ENTRY_FIELDS = ("title", "definition_de", "definition_en", "relevance", "tags")


class WikiStoreError(Exception):
    """Base class for all store-level rejections (caught by edit_server.py)."""


class NotFoundError(WikiStoreError):
    pass


class DuplicateError(WikiStoreError):
    pass


class ValidationError(WikiStoreError):
    pass


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _validate_component_name(value: object, *, label: str) -> str:
    """Reject a category/subcategory name that safe_path_component would have
    to rewrite -- fail closed instead of silently storing a mangled name the
    user did not ask for (safe_path_component itself is not called on the
    stored value; it is only used as the "would this be safe on disk?"
    check, since category/subcategory names do become path components in
    cmd_export)."""
    text = str(value).strip() if isinstance(value, str) else ""
    if not text:
        raise ValidationError(f"{label} darf nicht leer sein.")
    if safe_path_component(text) != text:
        raise ValidationError(
            f"{label} '{text}' enthaelt Zeichen, die nicht sicher als Pfadbestandteil "
            "verwendet werden koennen (z. B. Schraegstriche, Steuerzeichen, reservierte "
            "Namen). Bitte einen anderen Namen waehlen."
        )
    return text


def load(json_path: Path = JSON_PATH) -> dict[str, Any]:
    """Load and structurally validate the dataset (mirrors wikistub_seed_cli.load_json)."""
    data = read_json_object(json_path)
    root = data.get("MetaWiki")
    if not isinstance(root, dict):
        raise ValidationError("wikistub_seed.json must contain an object at MetaWiki")
    for category, subcategories in root.items():
        if not isinstance(category, str) or not isinstance(subcategories, dict):
            raise ValidationError("categories must be named JSON objects")
        for subcategory, entries in subcategories.items():
            if not isinstance(subcategory, str) or not isinstance(entries, list):
                raise ValidationError(f"invalid subcategory structure at {category}")
            for entry in entries:
                if not isinstance(entry, dict) or not isinstance(entry.get("title"), str):
                    raise ValidationError(f"invalid stub structure at {category}/{subcategory}")
    return data


def save(data: dict[str, Any], json_path: Path = JSON_PATH, backup_dir: Path = BACKUP_PATH) -> Path | None:
    """Backup the current on-disk file (if any), then atomically write *data*.
    Returns the backup path (or None if there was nothing to back up yet),
    which callers use to roll back if a post-write rebuild fails."""
    backup_path = backup_file(json_path, backup_dir, prefix="wikistub_seed", keep=10) if json_path.exists() else None
    atomic_write_json(json_path, data)
    return backup_path


def restore_from_backup(backup_path: Path, json_path: Path = JSON_PATH) -> None:
    """Inverse of save(): copy a previously-taken backup back over json_path.
    Used by edit_server.py when a post-write rebuild fails, so a bad write
    never lingers as the live dataset."""
    shutil.copy2(backup_path, json_path)


def find_category(data: dict[str, Any], category: str) -> str | None:
    """Diacritic/case-insensitive lookup of an existing category key
    (existing_mapping_key returns the input unchanged when nothing
    matches, so `key in root` is the correct "found it or not" test)."""
    root = data.get("MetaWiki", {})
    key = existing_mapping_key(root, category)
    return key if key in root else None


def find_subcategory(data: dict[str, Any], category: str, subcategory: str) -> str | None:
    cat_key = find_category(data, category)
    if cat_key is None:
        return None
    subcats = data["MetaWiki"][cat_key]
    key = existing_mapping_key(subcats, subcategory)
    return key if key in subcats else None


def find_entry(
    data: dict[str, Any], category: str, subcategory: str, title: str
) -> tuple[str, str, int, dict[str, Any]] | None:
    """Locate an entry by (category, subcategory, title) -- the same identity
    model the CLI and web_publisher/_build.py's stable-ID scheme already use
    (id = sha256(cat, sub, title)). Category/subcategory matching is
    diacritic/case-insensitive (existing_mapping_key), title matching is
    exact (identifier_key would treat two differently-capitalized titles as
    "the same stub", which is too aggressive for a rename target check)."""
    cat_key = find_category(data, category)
    if cat_key is None:
        return None
    sub_key = find_subcategory(data, cat_key, subcategory)
    if sub_key is None:
        return None
    entries = data["MetaWiki"][cat_key][sub_key]
    for index, entry in enumerate(entries):
        if isinstance(entry, dict) and entry.get("title") == title:
            return cat_key, sub_key, index, entry
    return None


def _reject_duplicate_title(data: dict[str, Any], category: str, subcategory: str, title: str, *, ignore_index: int | None = None) -> None:
    """Same-subcategory duplicate-title guard, run BEFORE any write -- this
    is exactly the collision class web_publisher/_build.py's stable-ID
    generation cannot tolerate (sha256(cat, sub, title) must be unique;
    Task 4's WikiStub-Aufbauprojekt backfill hit this for real with the DBT
    article). Rejecting it here means a bad create/rename never reaches
    disk, rather than relying on _build.py to catch it after the fact."""
    cat_key = find_category(data, category) or category
    sub_key = find_subcategory(data, cat_key, subcategory) or subcategory
    entries = data.get("MetaWiki", {}).get(cat_key, {}).get(sub_key, [])
    if not isinstance(entries, list):
        return
    for index, entry in enumerate(entries):
        if ignore_index is not None and index == ignore_index:
            continue
        if isinstance(entry, dict) and identifier_key(entry.get("title", "")) == identifier_key(title):
            raise DuplicateError(
                f"'{title}' existiert bereits in {cat_key}/{sub_key}."
            )


def create_category(data: dict[str, Any], category: str) -> str:
    """Create an empty category. Returns the stored key (reuses an existing
    equivalent key instead of creating an ASCII/diacritic near-duplicate,
    same policy as create_subcategory/create_entry)."""
    existing = find_category(data, category)
    if existing is not None:
        raise DuplicateError(f"Kategorie '{existing}' existiert bereits.")
    name = _validate_component_name(category, label="Kategorie")
    data.setdefault("MetaWiki", {})[name] = {}
    return name


def create_subcategory(data: dict[str, Any], category: str, subcategory: str) -> tuple[str, str]:
    """Create an empty subcategory under an EXISTING category. The category
    must already exist -- callers that want "create both in one step" use
    create_entry(), which auto-vivifies both (the common "just add an
    article under a brand new topic" flow); this function is for the
    explicit "add an empty subcategory" GUI action the ticket also asks
    for."""
    cat_key = find_category(data, category)
    if cat_key is None:
        raise NotFoundError(f"Kategorie '{category}' existiert nicht.")
    existing = find_subcategory(data, cat_key, subcategory)
    if existing is not None:
        raise DuplicateError(f"Subkategorie '{cat_key}/{existing}' existiert bereits.")
    name = _validate_component_name(subcategory, label="Subkategorie")
    data["MetaWiki"][cat_key][name] = []
    return cat_key, name


def create_entry(
    data: dict[str, Any], category: str, subcategory: str, fields: dict[str, Any]
) -> dict[str, Any]:
    """Create a new stub, auto-creating the category and/or subcategory if
    they do not exist yet (this is the "neue Kategorien und Unterartikel
    ERSTELLEN" path when done as one step from the GUI's "new article"
    form)."""
    title = str(fields.get("title", "")).strip()
    if not title:
        raise ValidationError("title darf nicht leer sein.")

    cat_key = find_category(data, category)
    if cat_key is None:
        cat_key = create_category(data, category)
    sub_key = find_subcategory(data, cat_key, subcategory)
    if sub_key is None:
        _, sub_key = create_subcategory(data, cat_key, subcategory)

    _reject_duplicate_title(data, cat_key, sub_key, title)

    entry = normalize_entry({k: v for k, v in fields.items() if k != "_category" and k != "_subcategory"})
    entry["title"] = title
    data["MetaWiki"][cat_key][sub_key].append(entry)
    return entry


def update_entry(
    data: dict[str, Any],
    category: str,
    subcategory: str,
    original_title: str,
    updates: dict[str, Any],
) -> dict[str, Any]:
    """Edit an existing stub in place (same category/subcategory -- moving
    an entry between categories is not part of this ticket's scope, only
    "AENDERN"). Uses language_model.merge_entry so any field this project
    does not know about (e.g. the private .WIKI fork's full_text/origin/
    source_path) survives untouched via public_entry()'s passthrough loop
    -- proven by tests/test_wiki_store.py's
    test_update_preserves_unknown_fields, which is this repo's half of the
    Teil-2 full_text guarantee the ticket asks for."""
    located = find_entry(data, category, subcategory, original_title)
    if located is None:
        raise NotFoundError(f"'{original_title}' nicht gefunden in {category}/{subcategory}.")
    cat_key, sub_key, index, existing = located

    new_title = str(updates.get("title", "")).strip() or existing.get("title", "")
    if new_title != existing.get("title"):
        _reject_duplicate_title(data, cat_key, sub_key, new_title, ignore_index=index)

    merged = merge_entry(existing, updates)
    if new_title:
        merged["title"] = new_title
    data["MetaWiki"][cat_key][sub_key][index] = merged
    return merged


def _append_trash(trash_path: Path, record: dict[str, Any]) -> None:
    records = _load_trash_raw(trash_path)
    records.append(record)
    atomic_write_json(trash_path, records)


def _load_trash_raw(trash_path: Path) -> list[dict[str, Any]]:
    if not trash_path.exists():
        return []
    try:
        payload = json.loads(trash_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    return payload if isinstance(payload, list) else []


def list_trash(trash_path: Path = TRASH_PATH) -> list[dict[str, Any]]:
    return _load_trash_raw(trash_path)


def delete_entry(
    data: dict[str, Any], category: str, subcategory: str, title: str, trash_path: Path = TRASH_PATH
) -> None:
    located = find_entry(data, category, subcategory, title)
    if located is None:
        raise NotFoundError(f"'{title}' nicht gefunden in {category}/{subcategory}.")
    cat_key, sub_key, index, entry = located
    _append_trash(trash_path, {
        "deleted_at": _now_iso(),
        "type": "entry",
        "category": cat_key,
        "subcategory": sub_key,
        "payload": entry,
    })
    del data["MetaWiki"][cat_key][sub_key][index]


def delete_subcategory(
    data: dict[str, Any], category: str, subcategory: str, trash_path: Path = TRASH_PATH
) -> None:
    cat_key = find_category(data, category)
    sub_key = find_subcategory(data, cat_key, subcategory) if cat_key else None
    if cat_key is None or sub_key is None:
        raise NotFoundError(f"Subkategorie '{category}/{subcategory}' nicht gefunden.")
    _append_trash(trash_path, {
        "deleted_at": _now_iso(),
        "type": "subcategory",
        "category": cat_key,
        "subcategory": sub_key,
        "payload": data["MetaWiki"][cat_key][sub_key],
    })
    del data["MetaWiki"][cat_key][sub_key]


def delete_category(data: dict[str, Any], category: str, trash_path: Path = TRASH_PATH) -> None:
    cat_key = find_category(data, category)
    if cat_key is None:
        raise NotFoundError(f"Kategorie '{category}' nicht gefunden.")
    _append_trash(trash_path, {
        "deleted_at": _now_iso(),
        "type": "category",
        "category": cat_key,
        "subcategory": None,
        "payload": data["MetaWiki"][cat_key],
    })
    del data["MetaWiki"][cat_key]


def restore_entry_from_trash(
    data: dict[str, Any], trash_path: Path, trash_index: int
) -> dict[str, Any]:
    """Inverse of delete_entry/delete_subcategory/delete_category: pop the
    record at *trash_index*, re-insert its payload at its original location
    (recreating the category/subcategory if they were also removed since),
    and return the restored payload. Refuses to silently overwrite a
    same-titled entry that already exists there (DuplicateError) rather
    than clobbering newer content -- the caller decides what to do next
    (e.g. rename, or delete the conflicting entry first)."""
    records = _load_trash_raw(trash_path)
    if trash_index < 0 or trash_index >= len(records):
        raise NotFoundError(f"Papierkorb-Eintrag {trash_index} existiert nicht.")
    record = records[trash_index]

    category = record.get("category")
    subcategory = record.get("subcategory")
    kind = record.get("type")
    payload = record.get("payload")

    if kind == "category":
        if find_category(data, category) is not None:
            raise DuplicateError(f"Kategorie '{category}' existiert bereits, kann nicht wiederhergestellt werden.")
        data.setdefault("MetaWiki", {})[category] = payload
    elif kind == "subcategory":
        cat_key = find_category(data, category)
        if cat_key is None:
            cat_key = create_category(data, category)
        if find_subcategory(data, cat_key, subcategory) is not None:
            raise DuplicateError(f"Subkategorie '{cat_key}/{subcategory}' existiert bereits, kann nicht wiederhergestellt werden.")
        data["MetaWiki"][cat_key][subcategory] = payload
    elif kind == "entry":
        cat_key = find_category(data, category)
        if cat_key is None:
            cat_key = create_category(data, category)
        sub_key = find_subcategory(data, cat_key, subcategory)
        if sub_key is None:
            _, sub_key = create_subcategory(data, cat_key, subcategory)
        title = payload.get("title", "") if isinstance(payload, dict) else ""
        _reject_duplicate_title(data, cat_key, sub_key, title)
        data["MetaWiki"][cat_key][sub_key].append(payload)
    else:
        raise ValidationError(f"Unbekannter Papierkorb-Eintragstyp: {kind!r}")

    del records[trash_index]
    atomic_write_json(trash_path, records)
    return payload
