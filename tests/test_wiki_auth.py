import tempfile
import time
import unittest
from pathlib import Path

import wiki_auth


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


class LoadSaveTests(unittest.TestCase):
    def test_load_auth_returns_none_when_file_absent(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "wiki_auth.json"
            self.assertIsNone(wiki_auth.load_auth(path))

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
        record_template = {"anonymous_permissions": None}
        combos = [
            (c, e, d)
            for c in (True, False)
            for e in (True, False)
            for d in (True, False)
        ]
        self.assertEqual(len(combos), 8)
        for create, edit, delete in combos:
            record = dict(record_template)
            record["anonymous_permissions"] = {"create": create, "edit": edit, "delete": delete}
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

    def test_malformed_anonymous_permissions_value_defaults_to_full(self):
        record = {"anonymous_permissions": "not-a-dict"}
        self.assertEqual(
            wiki_auth.compute_permissions(record, authenticated=False),
            wiki_auth.default_anonymous_permissions(),
        )


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
