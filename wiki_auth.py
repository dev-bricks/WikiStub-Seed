"""Password-gated permission model for the local WikiStub edit server
(T-20260819-782505468).

Spec, verbatim from the user via the ticket:
  - Creating new entries is always allowed by default.
  - Editing and deleting are allowed for anyone AS LONG AS no password has
    been set.
  - Once a password IS set, whoever set it controls what an anonymous
    visitor may still do -- anywhere from "everyone may do everything" down
    to read-only (create/edit/delete are independently revocable).
  - Deliberately only ONE password/role here, not multiple tokens or an
    admin hierarchy -- the user called that Enterprise shape "vielleicht
    etwas uebertrieben" and asked for it to be documented as a roadmap idea
    (see README's Roadmap section), not built.

Threat model, stated plainly rather than implied: the password hash defends
against a casual read of wiki_auth.json revealing a plaintext (possibly
reused) password. It does NOT defend against local filesystem access --
anyone who can read/write files on this machine can already read or replace
wiki_auth.json outright, bypassing the password entirely. This is a
shared-computer courtesy control, not a security boundary against a local
attacker with file access. Recovery from a forgotten password is therefore
also filesystem-level and documented as such: delete wiki_auth.json to
return to the default (no password, full rights for everyone).

Setting a password changes nothing else by itself -- "der Hinterleger
verteilt die Rechte" (the person who set it decides) is a SEPARATE action
(set_anonymous_permissions) from setting the password itself. A user who
sets a password expecting an immediate lockdown and finds nothing restricted
is not hitting a bug; this is documented in the README so it is not
surprising in practice.
"""
from __future__ import annotations

import hashlib
import hmac
import secrets
import time
from pathlib import Path
from typing import Any

from safe_io import JsonDataError, atomic_write_json, read_json_object

BASE_PATH = Path(__file__).parent.resolve()
AUTH_PATH = BASE_PATH / "wiki_auth.json"

ALGORITHM = "pbkdf2_sha256"
DEFAULT_ITERATIONS = 260_000
_SALT_BYTES = 16

PERMISSION_KEYS = ("create", "edit", "delete")


def default_anonymous_permissions() -> dict[str, bool]:
    """Everyone gets full rights until a password holder restricts this --
    also the effective permissions when no password is set at all."""
    return {"create": True, "edit": True, "delete": True}


def hash_password(password: str, *, salt: bytes | None = None, iterations: int = DEFAULT_ITERATIONS) -> dict[str, Any]:
    if not isinstance(password, str) or not password:
        raise ValueError("password darf nicht leer sein.")
    salt = salt if salt is not None else secrets.token_bytes(_SALT_BYTES)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return {
        "algorithm": ALGORITHM,
        "salt": salt.hex(),
        "iterations": iterations,
        "password_hash": digest.hex(),
    }


def verify_password(password: str, record: dict[str, Any]) -> bool:
    """Constant-time comparison against the stored hash -- recomputes with
    the record's own salt/iterations rather than assuming DEFAULT_ITERATIONS,
    so a future iteration-count bump does not break existing wiki_auth.json
    files."""
    if not isinstance(password, str) or not password:
        return False
    try:
        salt = bytes.fromhex(record["salt"])
        iterations = int(record["iterations"])
        expected = record["password_hash"]
    except (KeyError, TypeError, ValueError):
        return False
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(digest.hex(), expected)


def load_auth(path: Path = AUTH_PATH) -> dict[str, Any] | None:
    """Returns None when no password has been set (file absent) -- that is
    a normal, expected state, not an error."""
    if not path.exists():
        return None
    try:
        return read_json_object(path)
    except JsonDataError:
        return None


def save_auth(record: dict[str, Any], path: Path = AUTH_PATH) -> None:
    atomic_write_json(path, record)


def remove_auth(path: Path = AUTH_PATH) -> None:
    """Authenticated-session convenience for "remove the password again".
    The filesystem-delete-the-file path documented above stays the recovery
    route for a FORGOTTEN password (this function requires already being
    authenticated, so it cannot help there)."""
    path.unlink(missing_ok=True)


def set_password(password: str, *, path: Path = AUTH_PATH, existing: dict[str, Any] | None = None) -> dict[str, Any]:
    """Create or replace the password. Preserves anonymous_permissions
    across a password CHANGE (changing your password should not silently
    reset who is allowed to do what); a brand-new password (existing=None)
    starts at full anonymous rights, per default_anonymous_permissions()."""
    record = hash_password(password)
    record["anonymous_permissions"] = dict(
        existing.get("anonymous_permissions", default_anonymous_permissions())
        if existing
        else default_anonymous_permissions()
    )
    save_auth(record, path)
    return record


def set_anonymous_permissions(permissions: dict[str, Any], *, path: Path = AUTH_PATH, existing: dict[str, Any]) -> dict[str, Any]:
    """Authenticated-only: the password holder decides what an anonymous
    visitor may still do. Only accepts the three known keys; anything else
    in *permissions* is ignored rather than stored verbatim."""
    updated = dict(existing)
    current = dict(existing.get("anonymous_permissions", default_anonymous_permissions()))
    for key in PERMISSION_KEYS:
        if key in permissions:
            current[key] = bool(permissions[key])
    updated["anonymous_permissions"] = current
    save_auth(updated, path)
    return updated


def compute_permissions(auth_record: dict[str, Any] | None, *, authenticated: bool) -> dict[str, bool]:
    """The one place permission decisions are made -- edit_server.py must
    call this rather than re-deriving it, so the rule stays in one place.

    - No password set at all -> everyone has full rights (spec bullet 1+2).
    - Authenticated (knows the current password) -> always full rights; the
      password holder is the one "deciding" the anonymous level, they are
      not bound by their own restriction.
    - Password set, not authenticated -> whatever anonymous_permissions
      currently says (defaults to full until explicitly restricted)."""
    if auth_record is None:
        return default_anonymous_permissions()
    if authenticated:
        return {"create": True, "edit": True, "delete": True}
    stored = auth_record.get("anonymous_permissions")
    if not isinstance(stored, dict):
        return default_anonymous_permissions()
    return {key: bool(stored.get(key, True)) for key in PERMISSION_KEYS}


class SessionStore:
    """Minimal in-memory session tracker -- process lifetime only, never
    persisted to disk (a restart requires logging in again; this is a
    deliberate simplicity choice for a local single-user tool, not an
    oversight). Tokens are opaque, unguessable (secrets.token_urlsafe) and
    time-limited."""

    def __init__(self, ttl_seconds: float = 4 * 3600) -> None:
        self._ttl = ttl_seconds
        self._tokens: dict[str, float] = {}

    def create(self) -> str:
        token = secrets.token_urlsafe(32)
        self._tokens[token] = time.monotonic() + self._ttl
        return token

    def validate(self, token: str | None) -> bool:
        if not token:
            return False
        expiry = self._tokens.get(token)
        if expiry is None:
            return False
        if time.monotonic() > expiry:
            del self._tokens[token]
            return False
        return True

    def revoke(self, token: str | None) -> None:
        if token:
            self._tokens.pop(token, None)
