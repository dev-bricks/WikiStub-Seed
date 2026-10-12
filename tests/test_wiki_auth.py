import json
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

import wiki_auth


def _valid_auth_record(permissions=None):
    record = {
        "algorithm": wiki_auth.ALGORITHM,
        "salt": "00",
        "iterations": 1,
        "password_hash": "00" * 32,
    }
    if permissions is not None:
        record["anonymous_permissions"] = permissions
    return record


class HashingTests(unittest.TestCase):
    def test_verify_accepts_the_correct_password(self):
        record = wiki_auth.hash_password("correct-horse-battery-staple")
        self.assertTrue(wiki_auth.verify_password("correct-horse-battery-staple", record))

    def test_verify_rejects_a_wrong_password(self):
        record = wiki_auth.hash_password("correct-horse-battery-staple")
        self.assertFalse(wiki_auth.verify_password("wrong", record))

    def test_verify_rejects_empty_password(self):
        record = wiki_auth.hash_password("correct-horse-battery-staple")
        self.assertFalse(wiki_auth.verify_password("", record))

    def test_password_is_never_stored_in_plaintext(self):
        record = wiki_auth.hash_password("correct-horse-battery-staple")
        self.assertNotIn("correct-horse-battery-staple", str(record))
        self.assertNotEqual(record["password_hash"], "correct-horse-battery-staple")

    def test_two_hashes_of_the_same_password_use_different_salts(self):
        first = wiki_auth.hash_password("same-password")
        second = wiki_auth.hash_password("same-password")
        self.assertNotEqual(first["salt"], second["salt"])
        self.assertNotEqual(first["password_hash"], second["password_hash"])

    def test_set_password_requires_non_empty_string(self):
        with self.assertRaises(ValueError):
            wiki_auth.hash_password("")

    def test_hash_rejects_out_of_range_parameters_before_running_pbkdf2(self):
        for iterations in (0, -1, wiki_auth.MAX_ITERATIONS + 1, True):
            with self.subTest(iterations=iterations), self.assertRaises(ValueError):
                wiki_auth.hash_password("password", iterations=iterations)
        with self.assertRaises(ValueError):
            wiki_auth.hash_password("password", salt=b"x" * (wiki_auth._MAX_SALT_BYTES + 1))

    def test_empty_salt_and_one_iteration_remain_compatible_with_the_public_api(self):
        record = wiki_auth.hash_password("legacy-compatible", salt=b"", iterations=1)

        self.assertEqual(record["salt"], "")
        self.assertTrue(wiki_auth.verify_password("legacy-compatible", record))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "wiki_auth.json"
            wiki_auth.save_auth(record, path)
            self.assertEqual(wiki_auth.load_auth(path), record)


class LoadSaveTests(unittest.TestCase):
    def test_load_auth_returns_none_when_file_absent(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "wiki_auth.json"
            self.assertIsNone(wiki_auth.load_auth(path))

    def test_existing_malformed_json_fails_closed_instead_of_becoming_no_password(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "wiki_auth.json"
            path.write_text("{broken synthetic json", encoding="utf-8")
            before = path.read_bytes()

            with self.assertRaises(wiki_auth.AuthDataError):
                wiki_auth.load_auth(path)

            self.assertEqual(path.read_bytes(), before)

    def test_legacy_valid_record_without_permissions_keeps_default_policy(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "wiki_auth.json"
            record = _valid_auth_record()
            path.write_text(json.dumps(record), encoding="utf-8")

            loaded = wiki_auth.load_auth(path)

            self.assertEqual(loaded, record)
            self.assertEqual(
                wiki_auth.compute_permissions(loaded, authenticated=False),
                wiki_auth.default_anonymous_permissions(),
            )

    def test_existing_incomplete_or_invalid_hash_record_fails_closed(self):
        invalid_records = [
            {},
            {"algorithm": wiki_auth.ALGORITHM, "iterations": 1, "password_hash": "00" * 32},
            {"algorithm": wiki_auth.ALGORITHM, "salt": None, "iterations": 1, "password_hash": "00" * 32},
            {"algorithm": wiki_auth.ALGORITHM, "salt": "00", "iterations": 1},
            {"algorithm": wiki_auth.ALGORITHM, "salt": "00", "iterations": 1, "password_hash": None},
            {"algorithm": "unknown", "salt": "00", "iterations": 1, "password_hash": "00" * 32},
            {"algorithm": wiki_auth.ALGORITHM, "salt": "zz", "iterations": 1, "password_hash": "00" * 32},
            {"algorithm": wiki_auth.ALGORITHM, "salt": "00", "iterations": True, "password_hash": "00" * 32},
            {"algorithm": wiki_auth.ALGORITHM, "salt": "00", "iterations": 1, "password_hash": "00"},
            {
                "algorithm": wiki_auth.ALGORITHM,
                "salt": "00",
                "iterations": 1,
                "password_hash": "00" * 32,
                "anonymous_permissions": {"create": "false"},
            },
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "wiki_auth.json"
            for record in invalid_records:
                path.write_text(json.dumps(record), encoding="utf-8")
                with self.subTest(record=record), self.assertRaises(wiki_auth.AuthDataError):
                    wiki_auth.load_auth(path)

    def test_setting_password_does_not_replace_malformed_existing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "wiki_auth.json"
            path.write_text("{broken synthetic json", encoding="utf-8")
            before = path.read_bytes()

            with self.assertRaises(wiki_auth.AuthDataError):
                wiki_auth.set_password("replacement", path=path)

            self.assertEqual(path.read_bytes(), before)

    def test_set_password_then_load_roundtrips(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "wiki_auth.json"
            wiki_auth.set_password("hunter2", path=path)
            loaded = wiki_auth.load_auth(path)
            self.assertIsNotNone(loaded)
            self.assertTrue(wiki_auth.verify_password("hunter2", loaded))

    def test_new_password_starts_with_full_anonymous_rights(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "wiki_auth.json"
            record = wiki_auth.set_password("hunter2", path=path)
            self.assertEqual(record["anonymous_permissions"], wiki_auth.default_anonymous_permissions())

    def test_changing_password_preserves_existing_anonymous_permissions(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "wiki_auth.json"
            existing = wiki_auth.set_password("first", path=path)
            existing = wiki_auth.set_anonymous_permissions(
                {"edit": False, "delete": False}, path=path, existing=existing
            )
            changed = wiki_auth.set_password("second", path=path, existing=existing)
            self.assertEqual(changed["anonymous_permissions"], {"create": True, "edit": False, "delete": False})
            self.assertTrue(wiki_auth.verify_password("second", changed))
            self.assertFalse(wiki_auth.verify_password("first", changed))

    def test_remove_auth_deletes_the_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "wiki_auth.json"
            wiki_auth.set_password("hunter2", path=path)
            self.assertTrue(path.exists())
            wiki_auth.remove_auth(path)
            self.assertFalse(path.exists())

    def test_remove_auth_on_missing_file_does_not_raise(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "wiki_auth.json"
            wiki_auth.remove_auth(path)  # must not raise

    def test_default_path_is_used_only_for_a_marked_source_checkout(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text("[project]\nname='synthetic'\n", encoding="utf-8")
            (root / "wikistub_seed.json").write_text('{"MetaWiki": {}}', encoding="utf-8")
            with mock.patch.object(wiki_auth, "BASE_PATH", root):
                self.assertIsNone(wiki_auth.load_auth())
                record = wiki_auth.set_password("synthetic password")
                self.assertTrue(wiki_auth.verify_password("synthetic password", wiki_auth.load_auth()))
                updated = wiki_auth.set_anonymous_permissions({"edit": False}, existing=record)
                self.assertFalse(wiki_auth.load_auth()["anonymous_permissions"]["edit"])
                self.assertEqual(updated["anonymous_permissions"]["edit"], False)


class SetAnonymousPermissionsTests(unittest.TestCase):
    def test_only_known_keys_are_stored(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "wiki_auth.json"
            existing = wiki_auth.set_password("hunter2", path=path)
            updated = wiki_auth.set_anonymous_permissions(
                {"edit": False, "unknown_key": "ignored"}, path=path, existing=existing
            )
            self.assertEqual(
                updated["anonymous_permissions"], {"create": True, "edit": False, "delete": True}
            )
            self.assertNotIn("unknown_key", updated["anonymous_permissions"])

    def test_partial_update_leaves_other_keys_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "wiki_auth.json"
            existing = wiki_auth.set_password("hunter2", path=path)
            existing = wiki_auth.set_anonymous_permissions({"delete": False}, path=path, existing=existing)
            updated = wiki_auth.set_anonymous_permissions({"edit": False}, path=path, existing=existing)
            self.assertEqual(updated["anonymous_permissions"], {"create": True, "edit": False, "delete": False})

    def test_non_boolean_permission_values_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "wiki_auth.json"
            existing = wiki_auth.hash_password("password")
            for value in ("false", 0, 1, None):
                with self.subTest(value=value), self.assertRaises(wiki_auth.PermissionInputError):
                    wiki_auth.set_anonymous_permissions({"create": value}, path=path, existing=existing)
            for permissions in (None, ["create"], "create"):
                with self.subTest(permissions=permissions), self.assertRaises(wiki_auth.PermissionInputError):
                    wiki_auth.set_anonymous_permissions(permissions, path=path, existing=existing)
            self.assertFalse(path.exists())


class ComputePermissionsMatrixTests(unittest.TestCase):
    """The full permission matrix from the ticket's spec -- every combination
    the user's wording implies must be covered, not just the happy path."""

    def test_no_password_set_is_full_rights_for_everyone(self):
        self.assertEqual(
            wiki_auth.compute_permissions(None, authenticated=False),
            {"create": True, "edit": True, "delete": True},
        )

    def test_no_password_set_authenticated_flag_is_irrelevant(self):
        # authenticated=True with no auth_record at all should never happen
        # in edit_server.py (there is nothing to authenticate against), but
        # the function must still be safe/total.
        self.assertEqual(
            wiki_auth.compute_permissions(None, authenticated=True),
            {"create": True, "edit": True, "delete": True},
        )

    def test_password_set_default_anonymous_is_full_rights(self):
        record = {"anonymous_permissions": wiki_auth.default_anonymous_permissions()}
        self.assertEqual(
            wiki_auth.compute_permissions(record, authenticated=False),
            {"create": True, "edit": True, "delete": True},
        )

    def test_password_set_authenticated_is_always_full_rights_even_if_anonymous_is_read_only(self):
        record = {"anonymous_permissions": {"create": False, "edit": False, "delete": False}}
        self.assertEqual(
            wiki_auth.compute_permissions(record, authenticated=True),
            {"create": True, "edit": True, "delete": True},
        )

    def test_all_eight_anonymous_permission_combinations(self):
        combos = [
            (c, e, d)
            for c in (True, False)
            for e in (True, False)
            for d in (True, False)
        ]
        self.assertEqual(len(combos), 8)
        for create, edit, delete in combos:
            record = {"anonymous_permissions": {"create": create, "edit": edit, "delete": delete}}
            result = wiki_auth.compute_permissions(record, authenticated=False)
            self.assertEqual(result, {"create": create, "edit": edit, "delete": delete})

    def test_read_only_is_reachable_by_stepping_down_from_full(self):
        """'stufenweise zurueckstufen bis nur-lesend' -- explicitly confirm
        the all-False (read-only) floor is reachable, not just theoretically
        representable."""
        record = {"anonymous_permissions": {"create": False, "edit": False, "delete": False}}
        self.assertEqual(
            wiki_auth.compute_permissions(record, authenticated=False),
            {"create": False, "edit": False, "delete": False},
        )

    def test_missing_anonymous_permissions_key_defaults_to_full(self):
        record = {}
        self.assertEqual(
            wiki_auth.compute_permissions(record, authenticated=False),
            wiki_auth.default_anonymous_permissions(),
        )

    def test_malformed_anonymous_permissions_value_is_rejected(self):
        record = {"anonymous_permissions": "not-a-dict"}
        with self.assertRaises(wiki_auth.AuthDataError):
            wiki_auth.compute_permissions(record, authenticated=False)


class SessionStoreTests(unittest.TestCase):
    def test_created_token_validates(self):
        store = wiki_auth.SessionStore()
        token = store.create()
        self.assertTrue(store.validate(token))

    def test_unknown_token_does_not_validate(self):
        store = wiki_auth.SessionStore()
        self.assertFalse(store.validate("not-a-real-token"))

    def test_none_token_does_not_validate(self):
        store = wiki_auth.SessionStore()
        self.assertFalse(store.validate(None))

    def test_revoked_token_no_longer_validates(self):
        store = wiki_auth.SessionStore()
        token = store.create()
        store.revoke(token)
        self.assertFalse(store.validate(token))

    def test_expired_token_no_longer_validates(self):
        store = wiki_auth.SessionStore(ttl_seconds=0.05)
        token = store.create()
        time.sleep(0.1)
        self.assertFalse(store.validate(token))

    def test_two_created_tokens_are_different(self):
        store = wiki_auth.SessionStore()
        self.assertNotEqual(store.create(), store.create())


if __name__ == "__main__":
    unittest.main()
