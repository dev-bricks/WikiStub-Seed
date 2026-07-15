"""Small, dependency-free helpers for safe project file writes."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import tempfile
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any


_INVALID_PATH_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_WINDOWS_RESERVED = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}


def safe_path_component(value: object, *, max_length: int = 100) -> str:
    """Return one portable path component without traversal or device names."""
    original = unicodedata.normalize("NFC", str(value)).strip()
    cleaned = _INVALID_PATH_CHARS.sub("_", original).rstrip(" .")
    changed = cleaned != original

    if cleaned in {"", ".", ".."}:
        cleaned = "item"
        changed = True

    if cleaned.split(".", 1)[0].upper() in _WINDOWS_RESERVED:
        cleaned = f"_{cleaned}"
        changed = True

    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length].rstrip(" .") or "item"
        changed = True

    if changed:
        digest = hashlib.sha256(original.encode("utf-8")).hexdigest()[:8]
        prefix = cleaned[: max(1, max_length - len(digest) - 1)].rstrip(" .-") or "item"
        cleaned = f"{prefix}-{digest}"

    return cleaned


def atomic_write_text(path: Path, text: str, *, encoding: str = "utf-8") -> None:
    """Replace *path* atomically after a complete, flushed temporary write."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding=encoding, newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def atomic_write_json(path: Path, payload: Any) -> None:
    """Serialize JSON and atomically replace *path*."""
    atomic_write_text(
        Path(path), json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def backup_file(
    source: Path,
    backup_dir: Path,
    *,
    prefix: str,
    keep: int | None = None,
) -> Path | None:
    """Create a collision-resistant backup and optionally retain only *keep*."""
    source = Path(source)
    if not source.exists():
        return None

    backup_dir = Path(backup_dir)
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    destination = backup_dir / f"{prefix}_{stamp}{source.suffix}"
    shutil.copy2(source, destination)

    if keep is not None:
        backups = sorted(backup_dir.glob(f"{prefix}_*{source.suffix}"))
        for old in backups[:-keep]:
            old.unlink(missing_ok=True)

    return destination
