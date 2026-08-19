import http.client
import json
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock

import edit_server
from web_publisher import _build


def _sample_data():
    return {
        "MetaWiki": {
            "07_Informatik_KI": {
                "Software_Engineering": [
                    {
                        "title": "Domain-Driven Design",
                        "definitions": {"de": "Ein Modellierungsansatz.", "en": "A modeling approach."},
                        "definition_de": "Ein Modellierungsansatz.",
                        "definition_en": "A modeling approach.",
                        "relevance": "Strukturiert große Systeme.",
                        "relevance_i18n": {"de": "Strukturiert große Systeme."},
                        "tags": ["Informatik"],
                    }
                ]
            }
        }
    }


class EditServerTestCase(unittest.TestCase):
    """Spins up a real edit_server on 127.0.0.1:0 (OS-assigned port) against
    a temp-dir dataset/web_publisher/data, so every test exercises the real
    HTTP + JSON + auth + rebuild-or-rollback path end to end, not a mock of
    it."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        tmp_path = Path(self.tmp.name)
        self.json_path = tmp_path / "wikistub_seed.json"
        self.auth_path = tmp_path / "wiki_auth.json"
        self.trash_path = tmp_path / "wikistub_trash.json"
        self.backup_dir = tmp_path / "backups"
        self.out_dir = tmp_path / "data"
        self.out_dir.mkdir()
        self.out_data = self.out_dir / "wikistub_seed.json"
        self.out_index = self.out_dir / "search-index.json"
        self.json_path.write_text(json.dumps(_sample_data()), encoding="utf-8")

        self._build_patches = [
            mock.patch.object(_build, "SRC", self.json_path),
            mock.patch.object(_build, "OUT_DIR", self.out_dir),
            mock.patch.object(_build, "OUT_DATA", self.out_data),
            mock.patch.object(_build, "OUT_INDEX", self.out_index),
        ]
        for patch in self._build_patches:
            patch.start()

        self.server = edit_server.make_server(
            port=0, json_path=self.json_path, auth_path=self.auth_path,
            trash_path=self.trash_path, backup_dir=self.backup_dir,
        )
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)
        for patch in self._build_patches:
            patch.stop()
        self.tmp.cleanup()

    # ---- low-level request helper --------------------------------------

    def request(self, method, path, *, body=None, headers=None, cookie=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        try:
            hdrs = dict(headers or {})
            data = None
            if body is not None:
                data = json.dumps(body).encode("utf-8")
                hdrs.setdefault("Content-Type", "application/json")
            if cookie:
                hdrs["Cookie"] = f"{edit_server.SESSION_COOKIE_NAME}={cookie}"
            conn.request(method, path, body=data, headers=hdrs)
            resp = conn.getresponse()
            raw = resp.read()
            payload = json.loads(raw.decode("utf-8")) if raw else None
            set_cookie = resp.getheader("Set-Cookie")
            token = None
            if set_cookie and edit_server.SESSION_COOKIE_NAME in set_cookie:
                token = set_cookie.split(f"{edit_server.SESSION_COOKIE_NAME}=")[1].split(";")[0]
            return resp.status, payload, token
        finally:
            conn.close()

    def login(self, password):
        status, payload, token = self.request("POST", "/api/auth/login", body={"password": password})
        self.assertEqual(status, 200, payload)
        return token


class MakeServerHostGuardTests(unittest.TestCase):
    def test_refuses_to_bind_anything_other_than_localhost(self):
        with self.assertRaises(ValueError):
            edit_server.make_server(host="0.0.0.0", port=0)

    def test_refuses_wildcard_empty_host(self):
        with self.assertRaises(ValueError):
            edit_server.make_server(host="", port=0)


class PermissionsEndpointTests(EditServerTestCase):
    def test_no_password_set_reports_full_rights(self):
        status, payload, _ = self.request("GET", "/api/permissions")
        self.assertEqual(status, 200)
        self.assertEqual(payload, {
            "password_set": False, "authenticated": False,
            "create": True, "edit": True, "delete": True,
        })


class HostHeaderGuardTests(EditServerTestCase):
    def test_evil_host_header_is_rejected(self):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        try:
            conn.request("GET", "/api/permissions", headers={"Host": "evil.example"})
            resp = conn.getresponse()
            resp.read()
            self.assertEqual(resp.status, 400)
        finally:
            conn.close()


class ContentTypeGuardTests(EditServerTestCase):
    def test_missing_content_type_on_mutating_route_is_rejected(self):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        try:
            body = json.dumps({"category": "07_Informatik_KI", "subcategory": "Software_Engineering",
                                "entry": {"title": "X", "definition_de": "a", "definition_en": "b"}}).encode()
            conn.request("POST", "/api/entries", body=body)  # no Content-Type header
            resp = conn.getresponse()
            resp.read()
            self.assertEqual(resp.status, 415)
        finally:
            conn.close()

    def test_form_encoded_content_type_is_rejected(self):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        try:
            conn.request(
                "POST", "/api/entries", body=b"category=x&subcategory=y&title=z",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            resp = conn.getresponse()
            resp.read()
            self.assertEqual(resp.status, 415)
        finally:
            conn.close()


class CreateEntryTests(EditServerTestCase):
    def test_create_entry_succeeds_with_no_password_set(self):
        status, payload, _ = self.request(
            "POST", "/api/entries",
            body={"category": "07_Informatik_KI", "subcategory": "Software_Engineering",
                  "entry": {"title": "Refactoring", "definition_de": "Umbau.", "definition_en": "Restructuring."}},
        )
        self.assertEqual(status, 201, payload)
        self.assertEqual(payload["entry"]["title"], "Refactoring")

    def test_created_entry_is_persisted_and_rebuilt(self):
        self.request(
            "POST", "/api/entries",
            body={"category": "07_Informatik_KI", "subcategory": "Software_Engineering",
                  "entry": {"title": "Refactoring", "definition_de": "Umbau.", "definition_en": "Restructuring."}},
        )
        saved = json.loads(self.json_path.read_text(encoding="utf-8"))
        titles = [e["title"] for e in saved["MetaWiki"]["07_Informatik_KI"]["Software_Engineering"]]
        self.assertIn("Refactoring", titles)
        self.assertTrue(self.out_data.exists())
        self.assertTrue(self.out_index.exists())

    def test_create_entry_with_traversal_shaped_category_is_rejected(self):
        status, payload, _ = self.request(
            "POST", "/api/entries",
            body={"category": "../../etc", "subcategory": "x",
                  "entry": {"title": "Y", "definition_de": "a", "definition_en": "b"}},
        )
        self.assertEqual(status, 400, payload)

    def test_duplicate_title_rejected_with_409(self):
        status, payload, _ = self.request(
            "POST", "/api/entries",
            body={"category": "07_Informatik_KI", "subcategory": "Software_Engineering",
                  "entry": {"title": "Domain-Driven Design", "definition_de": "a", "definition_en": "b"}},
        )
        self.assertEqual(status, 409, payload)


class UpdateEntryTests(EditServerTestCase):
    def test_update_changes_definition(self):
        status, payload, _ = self.request(
            "PUT", "/api/entries",
            body={"category": "07_Informatik_KI", "subcategory": "Software_Engineering",
                  "original_title": "Domain-Driven Design", "entry": {"definition_de": "Neu."}},
        )
        self.assertEqual(status, 200, payload)
        self.assertEqual(payload["entry"]["definition_de"], "Neu.")

    def test_update_missing_entry_returns_404(self):
        status, payload, _ = self.request(
            "PUT", "/api/entries",
            body={"category": "07_Informatik_KI", "subcategory": "Software_Engineering",
                  "original_title": "Nichts da", "entry": {"definition_de": "x"}},
        )
        self.assertEqual(status, 404, payload)


class DeleteEntryAndTrashTests(EditServerTestCase):
    def test_delete_moves_to_trash_and_removes_from_data(self):
        status, payload, _ = self.request(
            "DELETE", "/api/entries",
            body={"category": "07_Informatik_KI", "subcategory": "Software_Engineering", "title": "Domain-Driven Design"},
        )
        self.assertEqual(status, 200, payload)
        saved = json.loads(self.json_path.read_text(encoding="utf-8"))
        self.assertEqual(saved["MetaWiki"]["07_Informatik_KI"]["Software_Engineering"], [])

        status, payload, _ = self.request("GET", "/api/trash")
        self.assertEqual(status, 200)
        self.assertEqual(len(payload["trash"]), 1)

    def test_restore_from_trash_reinserts_entry(self):
        self.request(
            "DELETE", "/api/entries",
            body={"category": "07_Informatik_KI", "subcategory": "Software_Engineering", "title": "Domain-Driven Design"},
        )
        status, payload, _ = self.request("POST", "/api/trash/restore", body={"index": 0})
        self.assertEqual(status, 200, payload)
        saved = json.loads(self.json_path.read_text(encoding="utf-8"))
        titles = [e["title"] for e in saved["MetaWiki"]["07_Informatik_KI"]["Software_Engineering"]]
        self.assertIn("Domain-Driven Design", titles)


class CategoryRoutesTests(EditServerTestCase):
    def test_create_category(self):
        status, payload, _ = self.request("POST", "/api/categories", body={"category": "13_Neu"})
        self.assertEqual(status, 201, payload)

    def test_create_subcategory(self):
        status, payload, _ = self.request(
            "POST", "/api/categories", body={"category": "07_Informatik_KI", "subcategory": "Neue_Sub"}
        )
        self.assertEqual(status, 201, payload)

    def test_delete_category_moves_to_trash(self):
        status, payload, _ = self.request("DELETE", "/api/categories", body={"category": "07_Informatik_KI"})
        self.assertEqual(status, 200, payload)
        saved = json.loads(self.json_path.read_text(encoding="utf-8"))
        self.assertNotIn("07_Informatik_KI", saved["MetaWiki"])


class AuthFlowTests(EditServerTestCase):
    def test_set_password_without_prior_auth_succeeds_when_none_exists(self):
        status, payload, _ = self.request("POST", "/api/auth/set-password", body={"new_password": "hunter2"})
        self.assertEqual(status, 200, payload)
        self.assertTrue(self.auth_path.exists())

    def test_login_with_correct_password_succeeds_and_sets_cookie(self):
        self.request("POST", "/api/auth/set-password", body={"new_password": "hunter2"})
        status, payload, token = self.request("POST", "/api/auth/login", body={"password": "hunter2"})
        self.assertEqual(status, 200, payload)
        self.assertTrue(payload["authenticated"])
        self.assertIsNotNone(token)

    def test_login_with_wrong_password_fails(self):
        self.request("POST", "/api/auth/set-password", body={"new_password": "hunter2"})
        status, payload, _ = self.request("POST", "/api/auth/login", body={"password": "wrong"})
        self.assertEqual(status, 401, payload)

    def test_login_when_no_password_set_returns_400(self):
        status, payload, _ = self.request("POST", "/api/auth/login", body={"password": "anything"})
        self.assertEqual(status, 400, payload)

    def test_changing_password_without_auth_is_rejected(self):
        self.request("POST", "/api/auth/set-password", body={"new_password": "hunter2"})
        status, payload, _ = self.request("POST", "/api/auth/set-password", body={"new_password": "newone"})
        self.assertEqual(status, 403, payload)

    def test_changing_password_with_valid_session_succeeds(self):
        self.request("POST", "/api/auth/set-password", body={"new_password": "hunter2"})
        token = self.login("hunter2")
        status, payload, _ = self.request(
            "POST", "/api/auth/set-password", body={"new_password": "newone"}, cookie=token
        )
        self.assertEqual(status, 200, payload)
        status, payload, _ = self.request("POST", "/api/auth/login", body={"password": "newone"})
        self.assertEqual(status, 200, payload)

    def test_logout_invalidates_the_session(self):
        self.request("POST", "/api/auth/set-password", body={"new_password": "hunter2"})
        token = self.login("hunter2")
        status, payload, _ = self.request("POST", "/api/auth/logout", body={}, cookie=token)
        self.assertEqual(status, 200, payload)
        status, payload, _ = self.request("GET", "/api/permissions")  # cookie was cleared client-side
        # send old token explicitly to prove it's now invalid server-side too
        status, payload, _ = self.request("GET", "/api/permissions", cookie=token)
        self.assertFalse(payload["authenticated"])

    def test_remove_password_requires_auth(self):
        self.request("POST", "/api/auth/set-password", body={"new_password": "hunter2"})
        status, payload, _ = self.request("POST", "/api/auth/remove-password", body={})
        self.assertEqual(status, 401, payload)

    def test_remove_password_with_auth_reverts_to_open(self):
        self.request("POST", "/api/auth/set-password", body={"new_password": "hunter2"})
        token = self.login("hunter2")
        status, payload, _ = self.request("POST", "/api/auth/remove-password", body={}, cookie=token)
        self.assertEqual(status, 200, payload)
        status, payload, _ = self.request("GET", "/api/permissions")
        self.assertFalse(payload["password_set"])
        self.assertEqual(payload["create"], True)
        self.assertEqual(payload["edit"], True)
        self.assertEqual(payload["delete"], True)


class PermissionMatrixHttpTests(EditServerTestCase):
    """HTTP-level confirmation that anonymous_permissions is actually
    enforced end to end, not just at the wiki_auth.compute_permissions()
    unit level."""

    def _set_password_and_restrict(self, permissions):
        self.request("POST", "/api/auth/set-password", body={"new_password": "hunter2"})
        token = self.login("hunter2")
        self.request("POST", "/api/auth/permissions", body=permissions, cookie=token)
        return token

    def test_anonymous_read_only_blocks_create(self):
        self._set_password_and_restrict({"create": False, "edit": False, "delete": False})
        status, payload, _ = self.request(
            "POST", "/api/entries",
            body={"category": "07_Informatik_KI", "subcategory": "Software_Engineering",
                  "entry": {"title": "X", "definition_de": "a", "definition_en": "b"}},
        )
        self.assertEqual(status, 403, payload)

    def test_anonymous_read_only_blocks_edit(self):
        self._set_password_and_restrict({"create": False, "edit": False, "delete": False})
        status, payload, _ = self.request(
            "PUT", "/api/entries",
            body={"category": "07_Informatik_KI", "subcategory": "Software_Engineering",
                  "original_title": "Domain-Driven Design", "entry": {"definition_de": "x"}},
        )
        self.assertEqual(status, 403, payload)

    def test_anonymous_read_only_blocks_delete(self):
        self._set_password_and_restrict({"create": False, "edit": False, "delete": False})
        status, payload, _ = self.request(
            "DELETE", "/api/entries",
            body={"category": "07_Informatik_KI", "subcategory": "Software_Engineering", "title": "Domain-Driven Design"},
        )
        self.assertEqual(status, 403, payload)

    def test_authenticated_session_bypasses_anonymous_restriction(self):
        token = self._set_password_and_restrict({"create": False, "edit": False, "delete": False})
        status, payload, _ = self.request(
            "DELETE", "/api/entries",
            body={"category": "07_Informatik_KI", "subcategory": "Software_Engineering", "title": "Domain-Driven Design"},
            cookie=token,
        )
        self.assertEqual(status, 200, payload)

    def test_create_only_anonymous_level_allows_create_but_not_edit(self):
        self._set_password_and_restrict({"create": True, "edit": False, "delete": False})
        status, _, _ = self.request(
            "POST", "/api/entries",
            body={"category": "07_Informatik_KI", "subcategory": "Software_Engineering",
                  "entry": {"title": "Neu", "definition_de": "a", "definition_en": "b"}},
        )
        self.assertEqual(status, 201)
        status, _, _ = self.request(
            "PUT", "/api/entries",
            body={"category": "07_Informatik_KI", "subcategory": "Software_Engineering",
                  "original_title": "Domain-Driven Design", "entry": {"definition_de": "x"}},
        )
        self.assertEqual(status, 403)


class RebuildRollbackTests(EditServerTestCase):
    def test_rebuild_failure_rolls_back_json_and_reports_500(self):
        before = self.json_path.read_bytes()
        with mock.patch.object(_build, "build", side_effect=ValueError("simulated duplicate ID")):
            status, payload, _ = self.request(
                "POST", "/api/entries",
                body={"category": "07_Informatik_KI", "subcategory": "Software_Engineering",
                      "entry": {"title": "WirdZurueckgerollt", "definition_de": "a", "definition_en": "b"}},
            )
        self.assertEqual(status, 500, payload)
        self.assertEqual(self.json_path.read_bytes(), before)


class StaticServingTests(EditServerTestCase):
    def test_index_html_is_served(self):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        try:
            conn.request("GET", "/index.html")
            resp = conn.getresponse()
            body = resp.read()
            self.assertEqual(resp.status, 200)
            self.assertIn(b"WikiStub-Seed", body)
        finally:
            conn.close()

    def test_data_responses_carry_no_store(self):
        self.out_data.write_text("{}", encoding="utf-8")
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        try:
            conn.request("GET", "/data/wikistub_seed.json")
            resp = conn.getresponse()
            resp.read()
            self.assertEqual(resp.status, 200)
            self.assertEqual(resp.getheader("Cache-Control"), "no-store")
        finally:
            conn.close()


if __name__ == "__main__":
    unittest.main()
