"""
Project ZIP analyzer for API Forge AI.

Pure-stdlib implementation (zipfile, os, re) with no external
dependencies, so it can be unit tested in isolation from the web
framework and has no supply-chain surface of its own.

Responsibilities:
  - Validate that an uploaded file is a well-formed ZIP archive.
  - Enforce limits that defend against zip bombs and path traversal.
  - Walk the archive's file list (never extracting anything to disk)
    and detect the project's language / framework from well-known
    marker files and a bounded, read-only peek at manifest contents.

This module never extracts, executes, or writes any entry from the
archive to disk. It only reads entry metadata and, for a small
allowlist of manifest files, the first 64KB of their text content.
"""
from __future__ import annotations

import io
import os
import re
import zipfile
from dataclasses import dataclass, field
from typing import Optional


class ZipValidationError(Exception):
    """Raised when an archive fails a hard safety check."""


@dataclass
class ZipAnalysisReport:
    valid: bool
    file_count: int
    total_uncompressed_bytes: int
    suspicious_entries: list = field(default_factory=list)
    detected_language: Optional[str] = None
    detected_framework: Optional[str] = None
    project_type: Optional[str] = None
    marker_files_found: list = field(default_factory=list)
    has_existing_api: bool = False
    warnings: list = field(default_factory=list)
    errors: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "valid": self.valid,
            "file_count": self.file_count,
            "total_uncompressed_bytes": self.total_uncompressed_bytes,
            "suspicious_entries": self.suspicious_entries,
            "detected_language": self.detected_language,
            "detected_framework": self.detected_framework,
            "project_type": self.project_type,
            "marker_files_found": self.marker_files_found,
            "has_existing_api": self.has_existing_api,
            "warnings": self.warnings,
            "errors": self.errors,
        }


# Entry names are rejected if they look like they could escape an
# extraction directory (absolute paths, drive letters, or `..`
# segments). We never extract to disk here, but any later extraction
# step must treat archives flagged by this check as unsupported.
_UNSAFE_PATTERN = re.compile(r"(^/|^[A-Za-z]:[\\/]|(^|/)\.\.(/|$))")


def _is_unsafe_path(name: str) -> bool:
    normalized = name.replace("\\", "/")
    return bool(_UNSAFE_PATTERN.search(normalized))


# (regex for the entry name, language, framework, project_type, is_api)
#
# Order is a priority list, most specific first: the first marker (in
# this order, not file-traversal order) that matches anything in the
# archive wins each field that is still unset. This keeps detection
# deterministic regardless of the order ZIP entries happen to appear in.
_MARKERS = [
    (r"(^|/)AndroidManifest\.xml$", "Kotlin/Java", "Android", "android-app", False),
    (r"(^|/)manage\.py$", "Python", "Django", "web-backend", True),
    (r"(^|/)wsgi\.py$", "Python", "WSGI (Flask/Django)", "web-backend", True),
    (r"(^|/)app\.py$", "Python", "Flask", "web-backend", True),
    (r"(^|/)main\.py$", "Python", "FastAPI/Generic", "web-backend", True),
    (r"(^|/)artisan$", "PHP", "Laravel", "web-backend", True),
    (r"(^|/)composer\.json$", "PHP", "PHP/Composer", "web-backend", False),
    (r"(^|/)package\.json$", "JavaScript/Node.js", "Node.js", "web-backend", False),
    (r"(^|/)pom\.xml$", "Java", "Maven", "backend", False),
    (r"(^|/)build\.gradle(\.kts)?$", "Kotlin/Java", "Gradle", "backend-or-android", False),
    (r"(^|/)Dockerfile$", None, "Docker", None, False),
    (r"(^|/)requirements\.txt$", "Python", None, None, False),
    (r"(^|/)index\.html$", "HTML", "Static site", "static-site", False),
]

_FRAMEWORK_IMPORT_HINTS = {
    "fastapi": "FastAPI",
    "flask": "Flask",
    "django": "Django",
    "express": "Express",
}

_API_FRAMEWORKS = {"FastAPI", "Flask", "Django", "Express"}


def analyze_zip_bytes(
    data: bytes,
    *,
    max_entries: int = 2000,
    max_uncompressed_bytes: int = 200 * 1024 * 1024,
) -> ZipAnalysisReport:
    """Analyze a ZIP archive's bytes without extracting anything to disk."""
    report = ZipAnalysisReport(valid=False, file_count=0, total_uncompressed_bytes=0)

    if not zipfile.is_zipfile(io.BytesIO(data)):
        report.errors.append("File is not a valid ZIP archive.")
        return report

    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        infos = zf.infolist()
        report.file_count = len(infos)

        if report.file_count == 0:
            report.errors.append("Archive contains no entries.")
            return report

        if report.file_count > max_entries:
            report.errors.append(
                f"Archive has {report.file_count} entries, exceeding the limit of {max_entries}."
            )
            return report

        total_size = 0
        marker_hits = set()
        all_names = []

        for info in infos:
            name = info.filename
            all_names.append(name)

            if _is_unsafe_path(name):
                report.suspicious_entries.append(name)
                continue

            total_size += info.file_size
            if total_size > max_uncompressed_bytes:
                report.errors.append(
                    "Archive exceeds the maximum allowed uncompressed size "
                    f"({max_uncompressed_bytes} bytes); rejected as a possible zip bomb."
                )
                return report

        report.total_uncompressed_bytes = total_size

        if report.suspicious_entries:
            report.errors.append(
                "Archive contains entries with unsafe paths (path traversal or "
                "absolute paths) and was rejected."
            )
            return report

        # Iterate markers in priority order (outer loop), not file
        # order, so detection doesn't depend on how the archive happened
        # to list its entries.
        for pattern, language, framework, project_type, is_api in _MARKERS:
            regex = re.compile(pattern)
            matched_names = [n for n in all_names if regex.search(n)]
            if not matched_names:
                continue
            marker_hits.update(matched_names)
            if language and not report.detected_language:
                report.detected_language = language
            if framework and not report.detected_framework:
                report.detected_framework = framework
            if project_type and not report.project_type:
                report.project_type = project_type
            if is_api:
                report.has_existing_api = True

        report.marker_files_found = sorted(marker_hits)

        # Refine Python/Node framework detection with a small, bounded,
        # read-only peek at manifest/entrypoint contents. Never executed.
        for name in all_names:
            base = os.path.basename(name).lower()
            if base in ("requirements.txt", "main.py", "app.py") and not _is_unsafe_path(name):
                try:
                    with zf.open(name) as fh:
                        content = fh.read(65536).decode("utf-8", errors="ignore").lower()
                except Exception:
                    continue
                for hint, framework_name in _FRAMEWORK_IMPORT_HINTS.items():
                    if hint in content:
                        report.detected_framework = framework_name
                        if framework_name in _API_FRAMEWORKS:
                            report.has_existing_api = True

        if not report.detected_language:
            report.warnings.append(
                "Could not confidently detect a project language from known marker files."
            )

        report.valid = True
        return report
