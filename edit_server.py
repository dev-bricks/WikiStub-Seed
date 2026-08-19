#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
edit_server.py - lokaler Edit-Modus fuer WikiStub-Seed (T-20260819-782505468)
==============================================================================

web_publisher ist eine reine Static-Site/PWA (app.js laedt per fetch(), kein
Server, kein Schreibzugriff). Fuer GUI-Editing (Artikel aendern, Kategorien/
Unterartikel anlegen, Kategorien/Artikel loeschen) braucht es einen lokalen
Server-Prozess, der (a) dieselben statischen Dateien ausliefert wie serve.py
(Vorbild: OneDrive/.WIKI/_wikistub/serve.py, die private Instanz) UND (b)
eine kleine JSON-API fuer die Schreiboperationen anbietet.

SICHERHEIT -- vor Aenderungen lesen:
  - Bindet AUSSCHLIESSLICH an 127.0.0.1, niemals konfigurierbar auf 0.0.0.0
    oder eine leere Adresse -- kein Cloud-/Netz-Exposure (Ticket-Vorgabe).
  - Jede schreibende Anfrage (POST/PUT/DELETE unter /api/) MUSS
    Content-Type: application/json tragen, sonst 415 -- das verhindert
    klassisches Cross-Site-Form-POST-CSRF (ein <form>-Tag kann keinen
    application/json-Body senden, ohne dass der Browser einen CORS-Preflight
    ausloest, den dieser Server nicht beantwortet). Kein CORS-Header wird je
    gesetzt: same-origin-only ist Absicht, kein Versehen.
  - Jede Anfrage MUSS einen Host-Header aus {localhost, 127.0.0.1} tragen,
    sonst 400 -- schliesst DNS-Rebinding (eine fremde Domain, die auf
    127.0.0.1 aufgeloest wird, aber im Host-Header ihren eigenen Namen
    traegt).
  - Session-Cookie ist HttpOnly + SameSite=Lax (kein Secure-Flag, da bewusst
    Klartext-HTTP auf localhost -- ein TLS-Zertifikat fuer 127.0.0.1 waere
    hier Overhead ohne echten Zusatznutzen; siehe wiki_auth.py's Threat-
    Model-Kommentar).
  - Rechte-Entscheidungen laufen AUSSCHLIESSLICH ueber
    wiki_auth.compute_permissions() -- keine zweite, abweichende Pruef-
    logik hier.
  - /data/*-Antworten tragen Cache-Control: no-store, damit ein Reload nach
    einem Edit nie eine veraltete Kopie zeigt (sw.js' networkFirst()-
    Strategie fuer /data/ macht das ohnehin unwahrscheinlich, aber dieser
    Header macht es explizit statt implizit).

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
SESSION_COOKIE_NAME = "wiki_session"
ALLOWED_HOSTS = {"localhost", "127.0.0.1"}


class ApiError(Exception):
    def __init__(self, status: int, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.message = message


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
            "Rebuild nach dem Schreiben fehlgeschlagen -- die Aenderung wurde "
            f"zurueckgerollt, es ist nichts verloren gegangen: {exc}",
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

    def __init__(self, *args: Any, directory: str | None = None, **kwargs: Any) -> None:
        super().__init__(*args, directory=directory or str(WEB_DIR), **kwargs)

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002 - stdlib signature
        pass  # keep test/CLI output quiet; errors still reach the client via JSON

    # ---- shared helpers ----------------------------------------------

    def _host_is_allowed(self) -> bool:
        host = (self.headers.get("Host") or "").split(":")[0].lower()
        return host in ALLOWED_HOSTS

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
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
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
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ApiError(400, f"Ungueltiges JSON: {exc}") from exc
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

    def do_GET(self) -> None:
        if not self._host_is_allowed():
            self.send_error(400, "Ungueltiger Host-Header.")
            return
        if self.path.split("?", 1)[0] == "/api/permissions":
            self._send_json(200, self._permissions_payload())
            return
        if self.path.split("?", 1)[0] == "/api/trash":
            self._handle_guarded(self._api_list_trash)
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
            self.send_error(400, "Ungueltiger Host-Header.")
            return
        path = self.path.split("?", 1)[0]
        method_name = self._ROUTES.get((self.command, path))
        if method_name is None:
            self.send_error(404, "Unbekannte Route.")
            return
        self._handle_guarded(getattr(self, method_name))

    def _handle_guarded(self, handler: Callable[[], None]) -> None:
        try:
            handler()
        except ApiError as exc:
            self._send_json(exc.status, {"error": exc.message})
        except wiki_store.NotFoundError as exc:
            self._send_json(404, {"error": str(exc)})
        except wiki_store.DuplicateError as exc:
            self._send_json(409, {"error": str(exc)})
        except wiki_store.ValidationError as exc:
            self._send_json(400, {"error": str(exc)})
        except wiki_store.JsonDataError as exc:  # pragma: no cover - safe_io re-export
            self._send_json(500, {"error": str(exc)})

    # ---- payload helpers --------------------------------------------

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

    def _api_create_entry(self) -> None:
        body = self._read_json_body()
        self._require(self._current_permissions(), "create")
        data = self._load()
        entry = wiki_store.create_entry(data, body.get("category", ""), body.get("subcategory", ""), body.get("entry", {}))
        self._commit(data)
        self._send_json(201, {"entry": entry})

    def _api_update_entry(self) -> None:
        body = self._read_json_body()
        self._require(self._current_permissions(), "edit")
        data = self._load()
        entry = wiki_store.update_entry(
            data, body.get("category", ""), body.get("subcategory", ""),
            body.get("original_title", ""), body.get("entry", {}),
        )
        self._commit(data)
        self._send_json(200, {"entry": entry})

    def _api_delete_entry(self) -> None:
        body = self._read_json_body()
        self._require(self._current_permissions(), "delete")
        data = self._load()
        wiki_store.delete_entry(data, body.get("category", ""), body.get("subcategory", ""), body.get("title", ""), self.server.trash_path)  # type: ignore[attr-defined]
        self._commit(data)
        self._send_json(200, {"deleted": True})

    # ---- category routes ------------------------------------------------

    def _api_create_category(self) -> None:
        body = self._read_json_body()
        self._require(self._current_permissions(), "create")
        data = self._load()
        if body.get("subcategory"):
            cat, sub = wiki_store.create_subcategory(data, body.get("category", ""), body["subcategory"])
            self._commit(data)
            self._send_json(201, {"category": cat, "subcategory": sub})
        else:
            cat = wiki_store.create_category(data, body.get("category", ""))
            self._commit(data)
            self._send_json(201, {"category": cat})

    def _api_delete_category(self) -> None:
        body = self._read_json_body()
        self._require(self._current_permissions(), "delete")
        data = self._load()
        if body.get("subcategory"):
            wiki_store.delete_subcategory(data, body.get("category", ""), body["subcategory"], self.server.trash_path)  # type: ignore[attr-defined]
        else:
            wiki_store.delete_category(data, body.get("category", ""), self.server.trash_path)  # type: ignore[attr-defined]
        self._commit(data)
        self._send_json(200, {"deleted": True})

    # ---- trash routes -----------------------------------------------

    def _api_list_trash(self) -> None:
        self._require(self._current_permissions(), "delete")
        self._send_json(200, {"trash": wiki_store.list_trash(self.server.trash_path)})  # type: ignore[attr-defined]

    def _api_restore_trash(self) -> None:
        body = self._read_json_body()
        self._require(self._current_permissions(), "delete")
        index = body.get("index")
        if not isinstance(index, int):
            raise ApiError(400, "index (Ganzzahl) erforderlich.")
        data = self._load()
        restored = wiki_store.restore_entry_from_trash(data, self.server.trash_path, index)  # type: ignore[attr-defined]
        self._commit(data)
        self._send_json(200, {"restored": restored})

    # ---- auth routes --------------------------------------------------

    def _api_login(self) -> None:
        body = self._read_json_body()
        auth_record = wiki_auth.load_auth(self.server.auth_path)  # type: ignore[attr-defined]
        if auth_record is None:
            raise ApiError(400, "Es ist kein Passwort hinterlegt.")
        if not wiki_auth.verify_password(str(body.get("password", "")), auth_record):
            raise ApiError(401, "Falsches Passwort.")
        token = self.server.session_store.create()  # type: ignore[attr-defined]
        self._send_json(200, self._permissions_payload_with_token(token), set_cookie=token)

    def _permissions_payload_with_token(self, token: str) -> dict[str, Any]:
        # Cookie is set by the caller before this executes on the real socket,
        # but _is_authenticated() reads self.headers, not the outgoing
        # Set-Cookie -- so we compute the post-login permissions explicitly.
        auth_record = wiki_auth.load_auth(self.server.auth_path)  # type: ignore[attr-defined]
        permissions = wiki_auth.compute_permissions(auth_record, authenticated=True)
        return {"password_set": True, "authenticated": True, **permissions}

    def _api_logout(self) -> None:
        self.server.session_store.revoke(self._session_token())  # type: ignore[attr-defined]
        self._send_json(200, {"authenticated": False}, clear_cookie=True)

    def _api_set_password(self) -> None:
        body = self._read_json_body()
        new_password = str(body.get("new_password", ""))
        if not new_password:
            raise ApiError(400, "new_password darf nicht leer sein.")
        existing = wiki_auth.load_auth(self.server.auth_path)  # type: ignore[attr-defined]
        if existing is not None and not self._is_authenticated():
            raise ApiError(403, "Zum Aendern des Passworts ist eine Anmeldung erforderlich.")
        wiki_auth.set_password(new_password, path=self.server.auth_path, existing=existing)  # type: ignore[attr-defined]
        self._send_json(200, {"password_set": True})

    def _api_remove_password(self) -> None:
        self._read_json_body()
        self._require_auth()
        wiki_auth.remove_auth(self.server.auth_path)  # type: ignore[attr-defined]
        self.server.session_store.revoke(self._session_token())  # type: ignore[attr-defined]
        self._send_json(200, {"password_set": False}, clear_cookie=True)

    def _api_set_anonymous_permissions(self) -> None:
        body = self._read_json_body()
        self._require_auth()
        existing = wiki_auth.load_auth(self.server.auth_path)  # type: ignore[attr-defined]
        if existing is None:
            raise ApiError(400, "Es ist kein Passwort hinterlegt.")
        updated = wiki_auth.set_anonymous_permissions(body, path=self.server.auth_path, existing=existing)  # type: ignore[attr-defined]
        self._send_json(200, {"anonymous_permissions": updated["anonymous_permissions"]})

    # ---- static serving: no-store for /data/ -------------------------

    def end_headers(self) -> None:
        # send_header() must run BEFORE end_headers() flushes the header
        # block -- send_head() (which emits data/ responses) already calls
        # end_headers() internally, so hooking end_headers() itself (rather
        # than post-processing send_head()'s return value) is the only
        # place this header reliably lands on every /data/ response.
        if self.path.split("?", 1)[0].startswith("/data/"):
            self.send_header("Cache-Control", "no-store")
        super().end_headers()


def make_server(
    *, host: str = "127.0.0.1", port: int = DEFAULT_PORT,
    json_path: Path = wiki_store.JSON_PATH, auth_path: Path = wiki_auth.AUTH_PATH,
    trash_path: Path = wiki_store.TRASH_PATH, backup_dir: Path = wiki_store.BACKUP_PATH,
) -> ThreadingHTTPServer:
    """Factory so tests can bind port=0 (OS-assigned free port) and inject
    temp-dir paths instead of the real instance's files."""
    if host not in ALLOWED_HOSTS:
        raise ValueError(f"edit_server darf nur an {ALLOWED_HOSTS} binden, nicht an {host!r}.")
    server = ThreadingHTTPServer((host, port), EditRequestHandler)
    server.session_store = wiki_auth.SessionStore()  # type: ignore[attr-defined]
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
