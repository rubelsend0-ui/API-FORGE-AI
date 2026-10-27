"""
Local filesystem storage for uploaded project archives.

Every project gets a server-generated UUID (see app.database); that
UUID, never the client-supplied filename, is used to build the path
on disk, so there is no path-traversal surface from user input here.
"""
from __future__ import annotations

import os
import re

_SAFE_ID = re.compile(r"^[a-f0-9-]{36}$")  # a uuid4 string


class StorageError(Exception):
    pass


def _zip_path(storage_dir: str, project_id: str) -> str:
    if not _SAFE_ID.match(project_id):
        raise StorageError("Invalid project id.")
    os.makedirs(storage_dir, exist_ok=True)
    return os.path.join(storage_dir, f"{project_id}.zip")


def save_zip(storage_dir: str, project_id: str, data: bytes) -> str:
    path = _zip_path(storage_dir, project_id)
    tmp_path = path + ".tmp"
    with open(tmp_path, "wb") as f:
        f.write(data)
    os.replace(tmp_path, path)
    return path


def load_zip(storage_dir: str, project_id: str) -> bytes:
    path = _zip_path(storage_dir, project_id)
    if not os.path.isfile(path):
        raise StorageError("No uploaded archive found for this project.")
    with open(path, "rb") as f:
        return f.read()


def zip_exists(storage_dir: str, project_id: str) -> bool:
    try:
        path = _zip_path(storage_dir, project_id)
    except StorageError:
        return False
    return os.path.isfile(path)
