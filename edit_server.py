#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
edit_server.py - lokaler Edit-Modus fuer WikiStub-Seed (T-20260819-782505468)
==============================================================================

web_publisher ist eine reine Static-Site/PWA (app.js laedt per fetch(), kein
Server, kein Schreibzugriff). Fuer GUI-Editing (Artikel aendern, Kategorien/
Unterartikel anlegen, Kategorien/Artikel loeschen) braucht es einen lokalen
Server-Prozess, der (a) die statischen Dateien von web_publisher/ ausliefert
UND (b) eine kleine JSON-API fuer die Schreiboperationen anbietet.

SICHERHEIT -- vor Aenderungen lesen:
  - Bindet AUSSCHLIESSLICH an 127.0.0.1, niemals konfigurierbar auf 0.0.0.0
    oder eine leere Adresse -- kein Cloud-/Netz-Exposure (Ticket-Vorgabe).
  - Jede schreibende Anfrage (POST/PUT/DELETE unter /api/) MUSS
    Content-Type: application/json tragen (415 bei Abweichung), ein gueltiges
    Content-Length <= MAX_JSON_BODY_BYTES (1 MiB, sonst 413) besitzen und
    darf kein Transfer-Encoding verwenden (411). Das verhindert klassisches
    Cross-Site-Form-POST-CSRF sowie unbegrenzte Speicherallokation. Kein
    CORS-Header wird je gesetzt: same-origin-only ist Absicht.
  - Jede Anfrage (GET/HEAD/POST/PUT/DELETE) MUSS einen strikt geprueften
    Host-Header aus {localhost, 127.0.0.1} (optional mit numerischem Port
    1..65535) tragen, sonst 400 -- schliesst DNS-Rebinding.
  - Session-Cookie ist HttpOnly + SameSite=Lax; bei Passwort-Rotation oder
    Passwort-Entfernung werden bestehende Sitzungen vollstaendig invalidiert.
  - Alle mutierenden API-Operationen sind ueber server.write_lock serialisiert,
    sodass parallele Anfragen auf ThreadingHTTPServer keine Schreib- oder
    Rebuild-Races ausloesen.
  - Rechte-Entscheidungen laufen AUSSCHLIESSLICH ueber
    wiki_auth.compute_permissions() -- keine zweite, abweichende Pruef-
    logik hier.
  - /data/*-Antworten tragen Cache-Control: no-store, damit ein Reload nach
    einem Edit nie eine veraltete Kopie zeigt.

SCHREIBABLAUF (jede mutierende API-Route): validieren -> wiki_store.save()
(legt Backup an, schreibt atomar) -> web_publisher/_build.build() aufrufen.
Schlaegt der Rebuild fehl (z. B. Titel-Kollision, die die Vorab-Pruefung
nicht abgedeckt hat), wird das JSON aus dem gerade angelegten Backup
wiederhergestellt und _build.build() erneut aufgerufen -- die live-Daten
zeigen dann wieder den letzten bekannten guten Stand, nie einen halb
geschriebenen. Der Client bekommt 500 mit einer klaren Fehlermeldung.

Nutzung:
    python edit_server.py [PORT]      # Default-Port 8879, oeffnet den Browser
"""
from __future__ import annotations

import json
import sys
import threading
import webbrowser
from http import cookies
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable

import wiki_auth
import wiki_store
from web_publisher import _build

BASE_PATH = Path(__file__).parent.resolve()
WEB_DIR = BASE_PATH / "web_publisher"
DEFAULT_PORT = 8879
MAX_JSON_BODY_BYTES = 1_048_576  # 1 MiB ceiling against local memory exhaustion
SESSION_COOKIE_NAME = "wiki_session"
ALLOWED_HOSTS = {"localhost", "127.0.0.1"}


class ApiError(Exception):
    def __init__(self, status: int, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.message = message


def _reject_json_constant(token: str) -> Any:
    raise ValueError(f"Non-standard JSON constant {token!r} is not allowed")


def _require_str(body: dict[str, Any], key: str, *, allow_empty: bool = True) -> str:
    value = body.get(key, "" if allow_empty else None)
    if not isinstance(value, str):
        raise ApiError(400, f"Feld '{key}' muss ein String sein.")
    if not allow_empty and not value:
        raise ApiError(400, f"{key} darf nicht leer sein.")
    return value


def _require_dict(body: dict[str, Any], key: str) -> dict[str, Any]:
    value = body.get(key)
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ApiError(400, f"Feld '{key}' muss ein JSON-Objekt sein.")
    return value


def _rebuild_or_rollback(backup_path: Path | None, json_path: Path) -> None:
    """Run web_publisher/_build.py's build() after a successful write; on
    ANY failure (not just the anticipated duplicate-ID ValueError -- defense
    in depth for failure modes this module's own pre-write checks did not
    anticipate), restore the just-taken backup and rebuild again from the
    known-good state before reporting the error."""
    try:
        _build.build()
    except Exception as exc:  # noqa: BLE001 - deliberately broad, see docstring
        if backup_path is not None:
            wiki_store.restore_from_backup(backup_path, json_path)
            try:
                _build.build()
            except Exception:
                pass  # best-effort: the JSON is restored even if data/ rebuild also fails
        raise ApiError(
            500,
            "Rebuild nach dem Schreiben fehlgeschlagen -- die Änderung wurde "
            "zurückgerollt, es ist nichts verloren gegangen.",
        ) from exc


def commit(data: dict[str, Any], json_path: Path, backup_dir: Path) -> None:
    """Shared save+rebuild-or-rollback sequence for every mutating route."""
    backup_path = wiki_store.save(data, json_path, backup_dir)
    _rebuild_or_rollback(backup_path, json_path)


class EditRequestHandler(SimpleHTTPRequestHandler):
    """Static file serving (inherited from SimpleHTTPRequestHandler, same
    hardened path-traversal handling as serve.py already relies on) plus a
    small JSON API under /api/. server_bind restricts the socket family;
    the actual localhost-only guarantee comes from main()'s bind address,
    not from anything in this class."""

    server_version = "WikiStubEditServer/1.0"
    timeout = 10

    def __init__(self, *args: Any, directory: str | None = None, **kwargs: Any) -> None:
        super().__init__(*args, directory=directory or str(WEB_DIR), **kwargs)

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002 - stdlib signature
        pass  # keep test/CLI output quiet; errors still reach the client via JSON

    # ---- shared helpers ----------------------------------------------

    def _host_is_allowed(self) -> bool:
        host_headers = self.headers.get_all("Host") or []
        if len(host_headers) != 1:
            return False
        raw_host = host_headers[0]
        if not raw_host or any(ord(ch) <= 0x20 or ord(ch) == 0x7F for ch in raw_host):
            return False
        if raw_host.count(":") > 1:
            return False
        if ":" in raw_host:
            hostname, port_str = raw_host.split(":", 1)
            if not port_str.isascii() or not port_str.isdigit():
                return False
            port = int(port_str)
            if not (1 <= port <= 65535):
                return False
        else:
            hostname = raw_host
        return hostname.lower() in ALLOWED_HOSTS

    def _session_token(self) -> str | None:
        raw = self.headers.get("Cookie")
        if not raw:
            return None
        jar = cookies.SimpleCookie()
        try:
            jar.load(raw)
        except cookies.CookieError:
            return None
        morsel = jar.get(SESSION_COOKIE_NAME)
        return morsel.value if morsel else None

    def _is_authenticated(self) -> bool:
        return self.server.session_store.validate(self._session_token())  # type: ignore[attr-defined]

    def _current_permissions(self) -> dict[str, bool]:
        auth_record = wiki_auth.load_auth(self.server.auth_path)  # type: ignore[attr-defined]
        return wiki_auth.compute_permissions(auth_record, authenticated=self._is_authenticated())

    def _send_json(self, status: int, payload: Any, *, set_cookie: str | None = None, clear_cookie: bool = False) -> None:
        body = json.dumps(payload, ensure_ascii=False, allow_nan=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        if set_cookie:
            self.send_header(
                "Set-Cookie", f"{SESSION_COOKIE_NAME}={set_cookie}; HttpOnly; SameSite=Lax; Path=/"
            )
        if clear_cookie:
            self.send_header(
                "Set-Cookie", f"{SESSION_COOKIE_NAME}=; HttpOnly; SameSite=Lax; Path=/; Max-Age=0"
            )
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self) -> dict[str, Any]:
        content_type = (self.headers.get("Content-Type") or "").split(";")[0].strip().lower()
        if content_type != "application/json":
            raise ApiError(415, "Content-Type muss application/json sein.")
        if self.headers.get("Transfer-Encoding") is not None:
            raise ApiError(411, "Content-Length erforderlich; Transfer-Encoding wird nicht unterstützt.")
        length_headers = self.headers.get_all("Content-Length") or []
        if len(length_headers) > 1:
            raise ApiError(400, "Mehrfache Content-Length-Header sind unzulässig.")
        raw_length = length_headers[0] if length_headers else None
        if raw_length is None or not raw_length.strip():
            return {}
        stripped_length = raw_length.strip()
        if not stripped_length.isascii() or not stripped_length.isdigit():
            raise ApiError(400, "Ungültiger Content-Length-Header.")
        length = int(stripped_length)
        if length == 0:
            return {}
        if length > MAX_JSON_BODY_BYTES:
            raise ApiError(413, f"JSON-Body überschreitet das Limit von {MAX_JSON_BODY_BYTES} Bytes.")
        raw = self.rfile.read(length)
        if len(raw) != length:
            raise ApiError(400, "Unvollständiger Request-Body.")
        try:
            payload = json.loads(raw.decode("utf-8"), parse_constant=_reject_json_constant)
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError, RecursionError) as exc:
            raise ApiError(400, f"Ungültiges JSON: {exc}") from exc
        if not isinstance(payload, dict):
            raise ApiError(400, "JSON-Body muss ein Objekt sein.")
        return payload

    def _require(self, permissions: dict[str, bool], key: str) -> None:
        if not permissions.get(key):
            raise ApiError(403, f"Diese Aktion ('{key}') ist derzeit nicht erlaubt.")

    def _require_auth(self) -> None:
        if not self._is_authenticated():
            raise ApiError(401, "Anmeldung erforderlich.")

    # ---- dispatch -------------------------------------------------------

    def do_HEAD(self) -> None:
        if not self._host_is_allowed():
            self.send_error(400, "Ungültiger Host-Header.")
            return
        path = self.path.split("?", 1)[0]
        if path.startswith("/api/"):
            self.send_error(405, "HEAD wird auf API-Routen nicht unterstützt.")
            return
        super().do_HEAD()

    def do_GET(self) -> None:
        if not self._host_is_allowed():
            self.send_error(400, "Ungültiger Host-Header.")
            return
        if self.path.split("?", 1)[0] == "/api/permissions":
            self._handle_guarded(self._api_permissions, serialize=True)
            return
        if self.path.split("?", 1)[0] == "/api/trash":
            self._handle_guarded(self._api_list_trash, serialize=True)
            return
        super().do_GET()

    def do_POST(self) -> None:
        self._dispatch_mutating()

    def do_PUT(self) -> None:
        self._dispatch_mutating()

    def do_DELETE(self) -> None:
        self._dispatch_mutating()

    _ROUTES: dict[tuple[str, str], str] = {
        ("POST", "/api/entries"): "_api_create_entry",
        ("PUT", "/api/entries"): "_api_update_entry",
        ("DELETE", "/api/entries"): "_api_delete_entry",
        ("POST", "/api/categories"): "_api_create_category",
        ("DELETE", "/api/categories"): "_api_delete_category",
        ("POST", "/api/trash/restore"): "_api_restore_trash",
        ("POST", "/api/auth/login"): "_api_login",
        ("POST", "/api/auth/logout"): "_api_logout",
        ("POST", "/api/auth/set-password"): "_api_set_password",
        ("POST", "/api/auth/remove-password"): "_api_remove_password",
        ("POST", "/api/auth/permissions"): "_api_set_anonymous_permissions",
    }

    def _dispatch_mutating(self) -> None:
        if not self._host_is_allowed():
            self.send_error(400, "Ungültiger Host-Header.")
            return
        path = self.path.split("?", 1)[0]
        method_name = self._ROUTES.get((self.command, path))
        if method_name is None:
            self.send_error(404, "Unbekannte Route.")
            return
        self._handle_guarded(getattr(self, method_name), serialize=True)

    def _handle_guarded(self, handler: Callable[[], None], *, serialize: bool = False) -> None:
        try:
            if serialize:
                with self.server.write_lock:  # type: ignore[attr-defined]
                    handler()
            else:
                handler()
        except ApiError as exc:
            self._send_json(exc.status, {"error": exc.message})
        except wiki_auth.AuthDataError:
            self._send_json(
                500,
                {"error": "Die lokale Authentifizierungsdatei ist ungültig. Zugriff bleibt gesperrt."},
            )
        except wiki_store.TrashDataError:
            self._send_json(
                500,
                {"error": "Die lokale Papierkorb-Datei ist ungültig. Bestehende Daten bleiben geschützt."},
            )
        except wiki_store.NotFoundError as exc:
            self._send_json(404, {"error": str(exc)})
        except wiki_store.DuplicateError as exc:
            self._send_json(409, {"error": str(exc)})
        except wiki_store.ValidationError as exc:
            self._send_json(400, {"error": str(exc)})
        except wiki_store.JsonDataError:
            self._send_json(
                500,
                {"error": "Die lokale Datensatz-Datei ist ungültig oder nicht lesbar."},
            )

    # ---- payload helpers --------------------------------------------

    def _api_permissions(self) -> None:
        self._send_json(200, self._permissions_payload())

    def _permissions_payload(self) -> dict[str, Any]:
        auth_record = wiki_auth.load_auth(self.server.auth_path)  # type: ignore[attr-defined]
        authenticated = self._is_authenticated()
        permissions = wiki_auth.compute_permissions(auth_record, authenticated=authenticated)
        return {
            "password_set": auth_record is not None,
            "authenticated": authenticated,
            **permissions,
        }

    # ---- entry routes -------------------------------------------------

    def _load(self) -> dict[str, Any]:
        return wiki_store.load(self.server.json_path)  # type: ignore[attr-defined]

    def _commit(self, data: dict[str, Any]) -> None:
        commit(data, self.server.json_path, self.server.backup_dir)  # type: ignore[attr-defined]

    def _snapshot_trash(self) -> tuple[bool, list[dict[str, Any]]]:
        trash_path: Path = self.server.trash_path  # type: ignore[attr-defined]
        if not trash_path.exists():
            return False, []
        return True, [dict(item) for item in wiki_store.list_trash(trash_path)]

    def _commit_or_restore_trash(
        self, data: dict[str, Any], trash_state: tuple[bool, list[dict[str, Any]]]
    ) -> None:
        try:
            self._commit(data)
        except Exception:
            trash_path: Path = self.server.trash_path  # type: ignore[attr-defined]
            had_trash, previous_records = trash_state
            try:
                if not had_trash:
                    trash_path.unlink(missing_ok=True)
                else:
                    wiki_store.atomic_write_json(trash_path, previous_records)
            except OSError:
                pass
            raise

    def _api_create_entry(self) -> None:
        body = self._read_json_body()
        self._require(self._current_permissions(), "create")
        category = _require_str(body, "category")
        subcategory = _require_str(body, "subcategory")
        entry_fields = _require_dict(body, "entry")
        data = self._load()
        entry = wiki_store.create_entry(data, category, subcategory, entry_fields)
        self._commit(data)
        self._send_json(201, {"entry": entry})

    def _api_update_entry(self) -> None:
        body = self._read_json_body()
        self._require(self._current_permissions(), "edit")
        category = _require_str(body, "category")
        subcategory = _require_str(body, "subcategory")
        original_title = _require_str(body, "original_title")
        entry_updates = _require_dict(body, "entry")
        data = self._load()
        entry = wiki_store.update_entry(
            data, category, subcategory, original_title, entry_updates,
        )
        self._commit(data)
        self._send_json(200, {"entry": entry})

    def _api_delete_entry(self) -> None:
        body = self._read_json_body()
        self._require(self._current_permissions(), "delete")
        category = _require_str(body, "category")
        subcategory = _require_str(body, "subcategory")
        title = _require_str(body, "title")
        data = self._load()
        trash_state = self._snapshot_trash()
        wiki_store.delete_entry(data, category, subcategory, title, self.server.trash_path)  # type: ignore[attr-defined]
        self._commit_or_restore_trash(data, trash_state)
        self._send_json(200, {"deleted": True})

    # ---- category routes ------------------------------------------------

    def _api_create_category(self) -> None:
        body = self._read_json_body()
        self._require(self._current_permissions(), "create")
        category = _require_str(body, "category")
        raw_sub = body.get("subcategory")
        if raw_sub is not None and not isinstance(raw_sub, str):
            raise ApiError(400, "Feld 'subcategory' muss ein String sein.")
        data = self._load()
        if raw_sub:
            cat, sub = wiki_store.create_subcategory(data, category, raw_sub)
            self._commit(data)
            self._send_json(201, {"category": cat, "subcategory": sub})
        else:
            cat = wiki_store.create_category(data, category)
            self._commit(data)
            self._send_json(201, {"category": cat})

    def _api_delete_category(self) -> None:
        body = self._read_json_body()
        self._require(self._current_permissions(), "delete")
        category = _require_str(body, "category")
        raw_sub = body.get("subcategory")
        if raw_sub is not None and not isinstance(raw_sub, str):
            raise ApiError(400, "Feld 'subcategory' muss ein String sein.")
        data = self._load()
        trash_state = self._snapshot_trash()
        if raw_sub:
            wiki_store.delete_subcategory(data, category, raw_sub, self.server.trash_path)  # type: ignore[attr-defined]
        else:
            wiki_store.delete_category(data, category, self.server.trash_path)  # type: ignore[attr-defined]
        self._commit_or_restore_trash(data, trash_state)
        self._send_json(200, {"deleted": True})

    # ---- trash routes -----------------------------------------------

    def _api_list_trash(self) -> None:
        self._require(self._current_permissions(), "delete")
        self._send_json(200, {"trash": wiki_store.list_trash(self.server.trash_path)})  # type: ignore[attr-defined]

    def _api_restore_trash(self) -> None:
        body = self._read_json_body()
        self._require(self._current_permissions(), "delete")
        index = body.get("index")
        if not isinstance(index, int) or isinstance(index, bool):
            raise ApiError(400, "index (Ganzzahl) erforderlich.")
        data = self._load()
        trash_state = self._snapshot_trash()
        restored = wiki_store.restore_entry_from_trash(data, self.server.trash_path, index)  # type: ignore[attr-defined]
        self._commit_or_restore_trash(data, trash_state)
        self._send_json(200, {"restored": restored})

    # ---- auth routes --------------------------------------------------

    def _api_login(self) -> None:
        body = self._read_json_body()
        auth_record = wiki_auth.load_auth(self.server.auth_path)  # type: ignore[attr-defined]
        if auth_record is None:
            raise ApiError(400, "Es ist kein Passwort hinterlegt.")
        password = body.get("password")
        if not isinstance(password, str) or not wiki_auth.verify_password(password, auth_record):
            raise ApiError(401, "Falsches Passwort.")
        token = self.server.session_store.create()  # type: ignore[attr-defined]
        self._send_json(200, self._permissions_payload_with_token(token), set_cookie=token)

    def _permissions_payload_with_token(self, token: str) -> dict[str, Any]:
        auth_record = wiki_auth.load_auth(self.server.auth_path)  # type: ignore[attr-defined]
        permissions = wiki_auth.compute_permissions(auth_record, authenticated=True)
        return {"password_set": True, "authenticated": True, **permissions}

    def _api_logout(self) -> None:
        self._read_json_body()
        self.server.session_store.revoke(self._session_token())  # type: ignore[attr-defined]
        self._send_json(200, {"authenticated": False}, clear_cookie=True)

    def _api_set_password(self) -> None:
        body = self._read_json_body()
        new_password = _require_str(body, "new_password", allow_empty=False)
        existing = wiki_auth.load_auth(self.server.auth_path)  # type: ignore[attr-defined]
        if existing is not None and not self._is_authenticated():
            raise ApiError(403, "Zum Ändern des Passworts ist eine Anmeldung erforderlich.")
        wiki_auth.set_password(new_password, path=self.server.auth_path, existing=existing)  # type: ignore[attr-defined]
        self.server.session_store.clear()  # type: ignore[attr-defined]
        rotated_cookie = (
            self.server.session_store.create() if existing is not None else None  # type: ignore[attr-defined]
        )
        self._send_json(200, {"password_set": True}, set_cookie=rotated_cookie)

    def _api_remove_password(self) -> None:
        self._read_json_body()
        self._require_auth()
        wiki_auth.remove_auth(self.server.auth_path)  # type: ignore[attr-defined]
        self.server.session_store.clear()  # type: ignore[attr-defined]
        self._send_json(200, {"password_set": False}, clear_cookie=True)

    def _api_set_anonymous_permissions(self) -> None:
        body = self._read_json_body()
        self._require_auth()
        existing = wiki_auth.load_auth(self.server.auth_path)  # type: ignore[attr-defined]
        if existing is None:
            raise ApiError(400, "Es ist kein Passwort hinterlegt.")
        try:
            updated = wiki_auth.set_anonymous_permissions(
                body, path=self.server.auth_path, existing=existing  # type: ignore[attr-defined]
            )
        except wiki_auth.PermissionInputError as exc:
            raise ApiError(400, str(exc)) from None
        self._send_json(200, {"anonymous_permissions": updated["anonymous_permissions"]})

    # ---- static serving: no-store for /data/ -------------------------

    def end_headers(self) -> None:
        if getattr(self, "path", "").split("?", 1)[0].startswith("/data/"):
            self.send_header("Cache-Control", "no-store")
        super().end_headers()


def make_server(
    *, host: str = "127.0.0.1", port: int = DEFAULT_PORT,
    json_path: Path = wiki_store.JSON_PATH, auth_path: Path = wiki_auth.AUTH_PATH,
    trash_path: Path = wiki_store.TRASH_PATH, backup_dir: Path = wiki_store.BACKUP_PATH,
) -> ThreadingHTTPServer:
    """Factory so tests can bind port=0 (OS-assigned free port) and inject
    temp-dir paths instead of the real instance's files."""
    if not isinstance(host, str) or host not in ALLOWED_HOSTS:
        raise ValueError(f"edit_server darf nur an {ALLOWED_HOSTS} binden, nicht an {host!r}.")
    if isinstance(port, bool) or not isinstance(port, int) or not (0 <= port <= 65535):
        raise ValueError(f"port muss zwischen 0 und 65535 liegen, nicht {port!r}.")
    server = ThreadingHTTPServer((host, port), EditRequestHandler)
    server.session_store = wiki_auth.SessionStore()  # type: ignore[attr-defined]
    server.write_lock = threading.Lock()  # type: ignore[attr-defined]
    server.auth_path = auth_path  # type: ignore[attr-defined]
    server.trash_path = trash_path  # type: ignore[attr-defined]
    server.json_path = json_path  # type: ignore[attr-defined]
    server.backup_dir = backup_dir  # type: ignore[attr-defined]
    return server


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT
    server = make_server(port=port)
    url = f"http://127.0.0.1:{port}/"
    print(f"[edit_server] {WEB_DIR} -> {url}")
    print("[edit_server] Nur lokal erreichbar (127.0.0.1). Strg+C zum Beenden.")
    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
