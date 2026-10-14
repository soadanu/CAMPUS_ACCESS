"""Engineer A tests: creation, validation, IDs, lookup, update, save/load."""

import json
import os
import tempfile
import unittest
from unittest import mock

from access_cards import storage


class StorageTestCase(unittest.TestCase):
    def setUp(self):
        storage.clear_requests()
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.path = os.path.join(folder.name, "requests.json")

    def write_file(self, content):
        with open(self.path, "w", encoding="utf-8") as file:
            file.write(content)

    def read_file(self):
        with open(self.path, "r", encoding="utf-8") as file:
            return file.read()


class TestCreateRequest(StorageTestCase):
    def test_valid_creation_has_all_five_fields(self):
        record = storage.create_request("F001", "visitor")
        self.assertEqual(
            record,
            {
                "id": "A001",
                "fellow_id": "F001",
                "card_type": "visitor",
                "status": "requested",
                "approved_by": None,
            },
        )

    def test_ids_increase_and_are_unique(self):
        ids = [storage.create_request("F001", "staff")["id"] for _ in range(3)]
        self.assertEqual(ids, ["A001", "A002", "A003"])

    def test_invalid_card_type_is_rejected_and_store_unchanged(self):
        for bad in ("guest", "Visitor", "", None, 5):
            with self.subTest(card_type=bad):
                with self.assertRaises(ValueError):
                    storage.create_request("F001", bad)
        self.assertEqual(storage.list_requests(), [])

    def test_blank_or_wrong_type_fellow_id_is_rejected(self):
        for bad in ("", "   ", " F001", "F001 ", None, 123, ["F001"]):
            with self.subTest(fellow_id=bad):
                with self.assertRaises(ValueError):
                    storage.create_request(bad, "student")
        self.assertEqual(storage.list_requests(), [])


class TestLookup(StorageTestCase):
    def test_malformed_and_unknown_ids_are_rejected(self):
        storage.create_request("F001", "visitor")
        bad_ids = [
            "", "A1", "a001", "B001", "A00X", "A001\n", " A001", None, 1,
            "A\u0660\u0660\u0661",  # Arabic-Indic digits
            "A\uff10\uff10\uff11",  # full-width digits
            "A999",                 # well formed but unknown
        ]
        for bad in bad_ids:
            with self.subTest(request_id=bad):
                with self.assertRaises(ValueError):
                    storage.get_request(bad)

    def test_get_request_returns_a_copy(self):
        storage.create_request("F001", "visitor")
        record = storage.get_request("A001")
        record["status"] = "returned"
        self.assertEqual(storage.get_request("A001")["status"], "requested")


class TestUpdateRequest(StorageTestCase):
    def test_issue_without_approver_is_rejected_and_record_unchanged(self):
        storage.create_request("F001", "visitor")
        before = storage.get_request("A001")
        for status, approver in (("issued", None), ("approved", ""), ("approved", "  ")):
            with self.subTest(status=status, approver=approver):
                with self.assertRaises(ValueError):
                    storage.update_request("A001", status, approver)
        self.assertEqual(storage.get_request("A001"), before)

    def test_invalid_status_and_unknown_id_are_rejected(self):
        storage.create_request("F001", "visitor")
        before = storage.get_request("A001")
        with self.assertRaises(ValueError):
            storage.update_request("A001", "teleported", "M01")
        with self.assertRaises(ValueError):
            storage.update_request("A002", "approved", "M01")
        self.assertEqual(storage.get_request("A001"), before)

    def test_valid_update_keeps_approver_when_not_passed(self):
        storage.create_request("F001", "visitor")
        storage.update_request("A001", "approved", "M01")
        record = storage.update_request("A001", "issued")
        self.assertEqual(record["status"], "issued")
        self.assertEqual(record["approved_by"], "M01")


class TestPersistence(StorageTestCase):
    def test_new_request_after_reload_is_a002(self):
        storage.create_request("F001", "visitor")
        storage.save_requests(self.path)
        storage.clear_requests()  # simulate restart
        self.assertEqual(storage.load_requests(self.path), 1)
        self.assertEqual(storage.create_request("F002", "staff")["id"], "A002")

    def test_round_trip_preserves_every_field(self):
        storage.create_request("F001", "visitor")
        storage.update_request("A001", "approved", "M01")
        expected = storage.list_requests()
        storage.save_requests(self.path)
        storage.clear_requests()
        storage.load_requests(self.path)
        self.assertEqual(storage.list_requests(), expected)

    def test_missing_file_is_a_first_run_not_an_error(self):
        self.assertEqual(storage.load_requests(self.path), 0)
        self.assertEqual(storage.list_requests(), [])

    def test_invalid_files_are_rejected_and_memory_is_preserved(self):
        good = {
            "id": "A001", "fellow_id": "F001", "card_type": "visitor",
            "status": "requested", "approved_by": None,
        }
        cases = {
            "malformed json": "{not json",
            "empty file": "",
            "top level not a list": json.dumps({"A001": good}),
            "record not an object": json.dumps(["A001"]),
            "missing key": json.dumps([{k: v for k, v in good.items() if k != "status"}]),
            "extra key": json.dumps([{**good, "color": "red"}]),
            "duplicate ids": json.dumps([good, good]),
            "bad card type": json.dumps([{**good, "card_type": "guest"}]),
            "bad status": json.dumps([{**good, "status": "lost"}]),
            "blank fellow id": json.dumps([{**good, "fellow_id": " "}]),
            "malformed id": json.dumps([{**good, "id": "A\u0660\u0660\u0661"}]),
            "issued without approver": json.dumps(
                [{**good, "status": "issued", "approved_by": None}]
            ),
            "requested with approver": json.dumps([{**good, "approved_by": "M01"}]),
        }
        for name, content in cases.items():
            with self.subTest(case=name):
                storage.clear_requests()
                storage.create_request("F900", "staff")
                before = storage.list_requests()
                self.write_file(content)
                with self.assertRaises(ValueError):
                    storage.load_requests(self.path)
                self.assertEqual(storage.list_requests(), before)
                self.assertEqual(self.read_file(), content)  # file untouched

    def test_failed_save_does_not_overwrite_a_valid_file(self):
        storage.create_request("F001", "visitor")
        storage.save_requests(self.path)
        original = self.read_file()

        storage.create_request("F002", "staff")
        with mock.patch("access_cards.storage.os.replace", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                storage.save_requests(self.path)

        self.assertEqual(self.read_file(), original)
        leftovers = [n for n in os.listdir(os.path.dirname(self.path)) if n.endswith(".tmp")]
        self.assertEqual(leftovers, [])


if __name__ == "__main__":
    unittest.main()
