import os
import sys
import tempfile
import unittest
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services import storage


class TestStorage(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.project_id = str(uuid.uuid4())

    def test_save_and_load_round_trip(self):
        data = b"PK\x03\x04fake zip bytes"
        path = storage.save_zip(self.tmp, self.project_id, data)
        self.assertTrue(os.path.isfile(path))
        self.assertTrue(storage.zip_exists(self.tmp, self.project_id))
        loaded = storage.load_zip(self.tmp, self.project_id)
        self.assertEqual(loaded, data)

    def test_load_missing_raises(self):
        with self.assertRaises(storage.StorageError):
            storage.load_zip(self.tmp, str(uuid.uuid4()))

    def test_rejects_unsafe_project_id(self):
        with self.assertRaises(storage.StorageError):
            storage.save_zip(self.tmp, "../../etc/passwd", b"x")

    def test_zip_exists_false_for_unsafe_id(self):
        self.assertFalse(storage.zip_exists(self.tmp, "../../etc/passwd"))


if __name__ == "__main__":
    unittest.main()
