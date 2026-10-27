import io
import sys
import os
import unittest
import zipfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.zip_analyzer import analyze_zip_bytes


def make_zip(files: dict) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, content in files.items():
            zf.writestr(name, content)
    return buf.getvalue()


class TestZipAnalyzer(unittest.TestCase):
    def test_rejects_non_zip(self):
        report = analyze_zip_bytes(b"not a zip file at all")
        self.assertFalse(report.valid)
        self.assertIn("not a valid ZIP archive", report.errors[0])

    def test_rejects_empty_zip(self):
        data = make_zip({})
        report = analyze_zip_bytes(data)
        self.assertFalse(report.valid)
        self.assertIn("no entries", report.errors[0])

    def test_rejects_path_traversal(self):
        data = make_zip({"../../etc/passwd": "root:x:0:0", "readme.txt": "hi"})
        report = analyze_zip_bytes(data)
        self.assertFalse(report.valid)
        self.assertIn("../../etc/passwd", report.suspicious_entries)

    def test_rejects_absolute_path(self):
        data = make_zip({"/etc/shadow": "x"})
        report = analyze_zip_bytes(data)
        self.assertFalse(report.valid)
        self.assertIn("/etc/shadow", report.suspicious_entries)

    def test_rejects_entry_count_over_limit(self):
        files = {f"file_{i}.txt": "x" for i in range(10)}
        data = make_zip(files)
        report = analyze_zip_bytes(data, max_entries=5)
        self.assertFalse(report.valid)
        self.assertIn("exceeding the limit", report.errors[0])

    def test_rejects_zip_bomb_like_size(self):
        data = make_zip({"big.txt": "a" * 5000})
        report = analyze_zip_bytes(data, max_uncompressed_bytes=1000)
        self.assertFalse(report.valid)
        self.assertTrue(any("maximum allowed uncompressed size" in e for e in report.errors))

    def test_detects_fastapi_project(self):
        data = make_zip({
            "requirements.txt": "fastapi==0.110.0\nuvicorn==0.29.0\n",
            "main.py": "from fastapi import FastAPI\napp = FastAPI()\n",
        })
        report = analyze_zip_bytes(data)
        self.assertTrue(report.valid)
        self.assertEqual(report.detected_language, "Python")
        self.assertEqual(report.detected_framework, "FastAPI")
        self.assertTrue(report.has_existing_api)

    def test_detects_flask_project(self):
        data = make_zip({
            "requirements.txt": "flask==3.0.0\n",
            "app.py": "from flask import Flask\napp = Flask(__name__)\n",
        })
        report = analyze_zip_bytes(data)
        self.assertTrue(report.valid)
        self.assertEqual(report.detected_framework, "Flask")
        self.assertTrue(report.has_existing_api)

    def test_detects_django_project(self):
        data = make_zip({
            "manage.py": "#!/usr/bin/env python\nimport django\n",
            "mysite/settings.py": "DEBUG = True\n",
        })
        report = analyze_zip_bytes(data)
        self.assertTrue(report.valid)
        self.assertEqual(report.detected_framework, "Django")
        self.assertTrue(report.has_existing_api)

    def test_detects_node_express_project(self):
        data = make_zip({
            "package.json": '{"dependencies": {"express": "^4.18.0"}}',
            "index.js": "const express = require('express');\n",
        })
        report = analyze_zip_bytes(data)
        self.assertTrue(report.valid)
        self.assertEqual(report.detected_language, "JavaScript/Node.js")

    def test_detects_android_project(self):
        data = make_zip({
            "app/build.gradle.kts": "plugins { id(\"com.android.application\") }",
            "app/src/main/AndroidManifest.xml": "<manifest></manifest>",
        })
        report = analyze_zip_bytes(data)
        self.assertTrue(report.valid)
        self.assertEqual(report.project_type, "android-app")
        self.assertFalse(report.has_existing_api)

    def test_detects_static_site_with_no_api(self):
        data = make_zip({
            "index.html": "<html><body>Hi</body></html>",
            "style.css": "body { color: black; }",
        })
        report = analyze_zip_bytes(data)
        self.assertTrue(report.valid)
        self.assertEqual(report.project_type, "static-site")
        self.assertFalse(report.has_existing_api)

    def test_unknown_project_emits_warning(self):
        data = make_zip({"notes.txt": "just some notes", "data.csv": "a,b,c"})
        report = analyze_zip_bytes(data)
        self.assertTrue(report.valid)
        self.assertIsNone(report.detected_language)
        self.assertTrue(len(report.warnings) >= 1)

    def test_to_dict_is_json_serializable(self):
        import json
        data = make_zip({"main.py": "from fastapi import FastAPI\napp = FastAPI()"})
        report = analyze_zip_bytes(data)
        serialized = json.dumps(report.to_dict())
        self.assertIn("FastAPI", serialized)


if __name__ == "__main__":
    unittest.main()
