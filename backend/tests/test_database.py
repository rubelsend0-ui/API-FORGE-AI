import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import database


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.conn = database.connect(":memory:")
        database.init_db(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_create_and_get_project(self):
        created = database.create_project(self.conn, "Demo Project", owner="dev@example.com")
        self.assertIsNotNone(created["id"])
        self.assertEqual(created["name"], "Demo Project")
        self.assertEqual(created["owner"], "dev@example.com")
        self.assertIsNone(created["analysis_report"])

        fetched = database.get_project(self.conn, created["id"])
        self.assertEqual(fetched, created)

    def test_get_missing_project_returns_none(self):
        self.assertIsNone(database.get_project(self.conn, "does-not-exist"))

    def test_list_projects_filters_by_owner(self):
        database.create_project(self.conn, "A", owner="alice@example.com")
        database.create_project(self.conn, "B", owner="bob@example.com")
        database.create_project(self.conn, "C", owner="alice@example.com")

        alice_projects = database.list_projects(self.conn, owner="alice@example.com")
        self.assertEqual(len(alice_projects), 2)
        self.assertTrue(all(p["owner"] == "alice@example.com" for p in alice_projects))

        all_projects = database.list_projects(self.conn)
        self.assertEqual(len(all_projects), 3)

    def test_set_upload_metadata(self):
        p = database.create_project(self.conn, "Demo", owner="dev@example.com")
        updated = database.set_upload_metadata(self.conn, p["id"], "source.zip", 12345)
        self.assertEqual(updated["zip_filename"], "source.zip")
        self.assertEqual(updated["zip_size_bytes"], 12345)

    def test_set_analysis_report_round_trips_json(self):
        p = database.create_project(self.conn, "Demo", owner="dev@example.com")
        report = {"valid": True, "detected_framework": "FastAPI", "has_existing_api": True}
        updated = database.set_analysis_report(self.conn, p["id"], report)
        self.assertEqual(updated["analysis_report"], report)
        self.assertIsNotNone(updated["analyzed_at"])


if __name__ == "__main__":
    unittest.main()
