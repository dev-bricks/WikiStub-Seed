import json
import tempfile
import unittest
from pathlib import Path

import wiki_store


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
                        "tags": ["Informatik", "Software Engineering"],
                    }
                ]
            }
        }
    }


class FindHelpersTests(unittest.TestCase):
    def test_find_category_exact_match(self):
        data = _sample_data()
        self.assertEqual(wiki_store.find_category(data, "07_Informatik_KI"), "07_Informatik_KI")

    def test_find_category_case_insensitive(self):
        data = _sample_data()
        self.assertEqual(wiki_store.find_category(data, "07_informatik_ki"), "07_Informatik_KI")

    def test_find_category_missing_returns_none(self):
        data = _sample_data()
        self.assertIsNone(wiki_store.find_category(data, "99_Nichts"))

    def test_find_entry_locates_by_triple(self):
        data = _sample_data()
        located = wiki_store.find_entry(data, "07_Informatik_KI", "Software_Engineering", "Domain-Driven Design")
        self.assertIsNotNone(located)
        cat, sub, index, entry = located
        self.assertEqual((cat, sub, index), ("07_Informatik_KI", "Software_Engineering", 0))
        self.assertEqual(entry["title"], "Domain-Driven Design")

    def test_find_entry_wrong_title_returns_none(self):
        data = _sample_data()
        self.assertIsNone(
            wiki_store.find_entry(data, "07_Informatik_KI", "Software_Engineering", "Does Not Exist")
        )


class CreateCategoryTests(unittest.TestCase):
    def test_creates_empty_category(self):
        data = _sample_data()
        key = wiki_store.create_category(data, "13_Neu")
        self.assertEqual(key, "13_Neu")
        self.assertEqual(data["MetaWiki"]["13_Neu"], {})

    def test_duplicate_category_rejected(self):
        data = _sample_data()
        with self.assertRaises(wiki_store.DuplicateError):
            wiki_store.create_category(data, "07_Informatik_KI")

    def test_duplicate_category_case_insensitive_rejected(self):
        data = _sample_data()
        with self.assertRaises(wiki_store.DuplicateError):
            wiki_store.create_category(data, "07_informatik_ki")

    def test_traversal_shaped_category_name_rejected(self):
        data = _sample_data()
        with self.assertRaises(wiki_store.ValidationError):
            wiki_store.create_category(data, "../../etc")

    def test_empty_category_name_rejected(self):
        data = _sample_data()
        with self.assertRaises(wiki_store.ValidationError):
            wiki_store.create_category(data, "   ")


class CreateSubcategoryTests(unittest.TestCase):
    def test_creates_under_existing_category(self):
        data = _sample_data()
        cat, sub = wiki_store.create_subcategory(data, "07_Informatik_KI", "Neue_Sub")
        self.assertEqual((cat, sub), ("07_Informatik_KI", "Neue_Sub"))
        self.assertEqual(data["MetaWiki"]["07_Informatik_KI"]["Neue_Sub"], [])

    def test_missing_category_rejected(self):
        data = _sample_data()
        with self.assertRaises(wiki_store.NotFoundError):
            wiki_store.create_subcategory(data, "99_Nichts", "X")

    def test_duplicate_subcategory_rejected(self):
        data = _sample_data()
        with self.assertRaises(wiki_store.DuplicateError):
            wiki_store.create_subcategory(data, "07_Informatik_KI", "Software_Engineering")

    def test_traversal_shaped_subcategory_name_rejected(self):
        data = _sample_data()
        with self.assertRaises(wiki_store.ValidationError):
            wiki_store.create_subcategory(data, "07_Informatik_KI", "..\\..\\windows")


class CreateEntryTests(unittest.TestCase):
    def test_creates_entry_in_existing_location(self):
        data = _sample_data()
        entry = wiki_store.create_entry(
            data, "07_Informatik_KI", "Software_Engineering",
            {"title": "Refactoring", "definition_de": "Code umbauen.", "definition_en": "Restructuring code."},
        )
        self.assertEqual(entry["title"], "Refactoring")
        titles = [e["title"] for e in data["MetaWiki"]["07_Informatik_KI"]["Software_Engineering"]]
        self.assertIn("Refactoring", titles)

    def test_auto_creates_category_and_subcategory(self):
        data = _sample_data()
        wiki_store.create_entry(
            data, "13_Neu", "Unterthema", {"title": "Erster Artikel", "definition_de": "x", "definition_en": "y"},
        )
        self.assertEqual(
            data["MetaWiki"]["13_Neu"]["Unterthema"][0]["title"], "Erster Artikel"
        )

    def test_duplicate_title_in_same_subcategory_rejected(self):
        data = _sample_data()
        with self.assertRaises(wiki_store.DuplicateError):
            wiki_store.create_entry(
                data, "07_Informatik_KI", "Software_Engineering",
                {"title": "Domain-Driven Design", "definition_de": "x", "definition_en": "y"},
            )

    def test_same_title_in_different_subcategory_is_allowed(self):
        data = _sample_data()
        entry = wiki_store.create_entry(
            data, "07_Informatik_KI", "Andere_Sub",
            {"title": "Domain-Driven Design", "definition_de": "x", "definition_en": "y"},
        )
        self.assertEqual(entry["title"], "Domain-Driven Design")

    def test_empty_title_rejected(self):
        data = _sample_data()
        with self.assertRaises(wiki_store.ValidationError):
            wiki_store.create_entry(data, "07_Informatik_KI", "Software_Engineering", {"title": "  "})


class UpdateEntryTests(unittest.TestCase):
    def test_updates_definition_in_place(self):
        data = _sample_data()
        updated = wiki_store.update_entry(
            data, "07_Informatik_KI", "Software_Engineering", "Domain-Driven Design",
            {"definition_de": "Neue Definition."},
        )
        self.assertEqual(updated["definition_de"], "Neue Definition.")
        self.assertEqual(updated["definition_en"], "A modeling approach.")  # untouched

    def test_missing_entry_raises_not_found(self):
        data = _sample_data()
        with self.assertRaises(wiki_store.NotFoundError):
            wiki_store.update_entry(
                data, "07_Informatik_KI", "Software_Engineering", "Nichts da", {"definition_de": "x"}
            )

    def test_rename_changes_title(self):
        data = _sample_data()
        updated = wiki_store.update_entry(
            data, "07_Informatik_KI", "Software_Engineering", "Domain-Driven Design",
            {"title": "DDD"},
        )
        self.assertEqual(updated["title"], "DDD")
        titles = [e["title"] for e in data["MetaWiki"]["07_Informatik_KI"]["Software_Engineering"]]
        self.assertEqual(titles, ["DDD"])

    def test_rename_onto_existing_sibling_title_is_rejected(self):
        data = _sample_data()
        wiki_store.create_entry(
            data, "07_Informatik_KI", "Software_Engineering",
            {"title": "Clean Code", "definition_de": "x", "definition_en": "y"},
        )
        with self.assertRaises(wiki_store.DuplicateError):
            wiki_store.update_entry(
                data, "07_Informatik_KI", "Software_Engineering", "Domain-Driven Design",
                {"title": "Clean Code"},
            )
        # Nothing was mutated by the rejected rename.
        titles = sorted(e["title"] for e in data["MetaWiki"]["07_Informatik_KI"]["Software_Engineering"])
        self.assertEqual(titles, ["Clean Code", "Domain-Driven Design"])

    def test_update_preserves_unknown_fields(self):
        """Teil-2 insurance: the private .WIKI fork's full_text/origin/
        source_path fields must survive an update that never mentions
        them -- this is the public repo's half of the "editing must not
        destroy the full-text field" requirement."""
        data = _sample_data()
        data["MetaWiki"]["07_Informatik_KI"]["Software_Engineering"][0]["full_text"] = "== Voller Artikeltext ==\n..."
        data["MetaWiki"]["07_Informatik_KI"]["Software_Engineering"][0]["origin"] = "wiki"
        data["MetaWiki"]["07_Informatik_KI"]["Software_Engineering"][0]["source_path"] = "bwl/ddd.txt"

        updated = wiki_store.update_entry(
            data, "07_Informatik_KI", "Software_Engineering", "Domain-Driven Design",
            {"definition_de": "Nur die Kurzdefinition geaendert."},
        )

        self.assertEqual(updated["full_text"], "== Voller Artikeltext ==\n...")
        self.assertEqual(updated["origin"], "wiki")
        self.assertEqual(updated["source_path"], "bwl/ddd.txt")
        self.assertEqual(updated["definition_de"], "Nur die Kurzdefinition geaendert.")


class DeleteEntryTests(unittest.TestCase):
    def test_delete_removes_from_data_and_writes_to_trash(self):
        data = _sample_data()
        with tempfile.TemporaryDirectory() as tmp:
            trash_path = Path(tmp) / "trash.json"
            wiki_store.delete_entry(data, "07_Informatik_KI", "Software_Engineering", "Domain-Driven Design", trash_path)
            self.assertEqual(data["MetaWiki"]["07_Informatik_KI"]["Software_Engineering"], [])
            trash = wiki_store.list_trash(trash_path)
            self.assertEqual(len(trash), 1)
            self.assertEqual(trash[0]["type"], "entry")
            self.assertEqual(trash[0]["payload"]["title"], "Domain-Driven Design")

    def test_delete_missing_entry_raises_not_found(self):
        data = _sample_data()
        with tempfile.TemporaryDirectory() as tmp:
            trash_path = Path(tmp) / "trash.json"
            with self.assertRaises(wiki_store.NotFoundError):
                wiki_store.delete_entry(data, "07_Informatik_KI", "Software_Engineering", "Nichts da", trash_path)

    def test_delete_never_hard_deletes(self):
        """The payload in trash is byte-for-byte the deleted entry, not a
        summary -- restore must be able to reproduce it exactly."""
        data = _sample_data()
        original = dict(data["MetaWiki"]["07_Informatik_KI"]["Software_Engineering"][0])
        with tempfile.TemporaryDirectory() as tmp:
            trash_path = Path(tmp) / "trash.json"
            wiki_store.delete_entry(data, "07_Informatik_KI", "Software_Engineering", "Domain-Driven Design", trash_path)
            trash = wiki_store.list_trash(trash_path)
            self.assertEqual(trash[0]["payload"], original)


class DeleteSubcategoryAndCategoryTests(unittest.TestCase):
    def test_delete_subcategory_moves_whole_list_to_trash(self):
        data = _sample_data()
        with tempfile.TemporaryDirectory() as tmp:
            trash_path = Path(tmp) / "trash.json"
            wiki_store.delete_subcategory(data, "07_Informatik_KI", "Software_Engineering", trash_path)
            self.assertNotIn("Software_Engineering", data["MetaWiki"]["07_Informatik_KI"])
            trash = wiki_store.list_trash(trash_path)
            self.assertEqual(trash[0]["type"], "subcategory")
            self.assertEqual(len(trash[0]["payload"]), 1)

    def test_delete_category_moves_whole_subtree_to_trash(self):
        data = _sample_data()
        with tempfile.TemporaryDirectory() as tmp:
            trash_path = Path(tmp) / "trash.json"
            wiki_store.delete_category(data, "07_Informatik_KI", trash_path)
            self.assertNotIn("07_Informatik_KI", data["MetaWiki"])
            trash = wiki_store.list_trash(trash_path)
            self.assertEqual(trash[0]["type"], "category")

    def test_delete_missing_subcategory_raises_not_found(self):
        data = _sample_data()
        with tempfile.TemporaryDirectory() as tmp:
            trash_path = Path(tmp) / "trash.json"
            with self.assertRaises(wiki_store.NotFoundError):
                wiki_store.delete_subcategory(data, "07_Informatik_KI", "Nichts", trash_path)

    def test_delete_missing_category_raises_not_found(self):
        data = _sample_data()
        with tempfile.TemporaryDirectory() as tmp:
            trash_path = Path(tmp) / "trash.json"
            with self.assertRaises(wiki_store.NotFoundError):
                wiki_store.delete_category(data, "99_Nichts", trash_path)


class RestoreFromTrashTests(unittest.TestCase):
    def test_restore_entry_reinserts_it(self):
        data = _sample_data()
        with tempfile.TemporaryDirectory() as tmp:
            trash_path = Path(tmp) / "trash.json"
            wiki_store.delete_entry(data, "07_Informatik_KI", "Software_Engineering", "Domain-Driven Design", trash_path)
            restored = wiki_store.restore_entry_from_trash(data, trash_path, 0)
            self.assertEqual(restored["title"], "Domain-Driven Design")
            titles = [e["title"] for e in data["MetaWiki"]["07_Informatik_KI"]["Software_Engineering"]]
            self.assertEqual(titles, ["Domain-Driven Design"])
            self.assertEqual(wiki_store.list_trash(trash_path), [])

    def test_restore_entry_recreates_missing_subcategory(self):
        data = _sample_data()
        with tempfile.TemporaryDirectory() as tmp:
            trash_path = Path(tmp) / "trash.json"
            wiki_store.delete_entry(data, "07_Informatik_KI", "Software_Engineering", "Domain-Driven Design", trash_path)
            wiki_store.delete_subcategory(data, "07_Informatik_KI", "Software_Engineering", trash_path)
            # Trash now: [entry-record, subcategory-record]; restore the subcategory first.
            wiki_store.restore_entry_from_trash(data, trash_path, 0)
            self.assertIn("Software_Engineering", data["MetaWiki"]["07_Informatik_KI"])

    def test_restore_category_conflict_raises_duplicate(self):
        data = _sample_data()
        with tempfile.TemporaryDirectory() as tmp:
            trash_path = Path(tmp) / "trash.json"
            wiki_store.delete_category(data, "07_Informatik_KI", trash_path)
            wiki_store.create_category(data, "07_Informatik_KI")  # something new took the name
            with self.assertRaises(wiki_store.DuplicateError):
                wiki_store.restore_entry_from_trash(data, trash_path, 0)

    def test_restore_entry_title_conflict_raises_duplicate(self):
        data = _sample_data()
        with tempfile.TemporaryDirectory() as tmp:
            trash_path = Path(tmp) / "trash.json"
            wiki_store.delete_entry(data, "07_Informatik_KI", "Software_Engineering", "Domain-Driven Design", trash_path)
            wiki_store.create_entry(
                data, "07_Informatik_KI", "Software_Engineering",
                {"title": "Domain-Driven Design", "definition_de": "andere", "definition_en": "other"},
            )
            with self.assertRaises(wiki_store.DuplicateError):
                wiki_store.restore_entry_from_trash(data, trash_path, 0)

    def test_restore_out_of_range_index_raises_not_found(self):
        data = _sample_data()
        with tempfile.TemporaryDirectory() as tmp:
            trash_path = Path(tmp) / "trash.json"
            with self.assertRaises(wiki_store.NotFoundError):
                wiki_store.restore_entry_from_trash(data, trash_path, 0)


class SaveAndRollbackTests(unittest.TestCase):
    def test_save_creates_backup_of_previous_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            json_path = Path(tmp) / "wikistub_seed.json"
            backup_dir = Path(tmp) / "backups"
            json_path.write_text(json.dumps({"MetaWiki": {}}), encoding="utf-8")

            backup_path = wiki_store.save({"MetaWiki": {"X": {}}}, json_path, backup_dir)

            self.assertIsNotNone(backup_path)
            self.assertEqual(json.loads(backup_path.read_text(encoding="utf-8")), {"MetaWiki": {}})
            self.assertEqual(json.loads(json_path.read_text(encoding="utf-8")), {"MetaWiki": {"X": {}}})

    def test_save_with_no_existing_file_returns_none_backup(self):
        with tempfile.TemporaryDirectory() as tmp:
            json_path = Path(tmp) / "wikistub_seed.json"
            backup_dir = Path(tmp) / "backups"
            backup_path = wiki_store.save({"MetaWiki": {}}, json_path, backup_dir)
            self.assertIsNone(backup_path)

    def test_restore_from_backup_reverts_a_bad_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            json_path = Path(tmp) / "wikistub_seed.json"
            backup_dir = Path(tmp) / "backups"
            json_path.write_text(json.dumps({"MetaWiki": {"good": {}}}), encoding="utf-8")

            backup_path = wiki_store.save({"MetaWiki": {"bad": {}}}, json_path, backup_dir)
            wiki_store.restore_from_backup(backup_path, json_path)

            self.assertEqual(json.loads(json_path.read_text(encoding="utf-8")), {"MetaWiki": {"good": {}}})


if __name__ == "__main__":
    unittest.main()
