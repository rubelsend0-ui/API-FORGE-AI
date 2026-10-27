"""
Minimal SQLite persistence layer for API Forge AI.

Deliberately dependency-free (stdlib `sqlite3` only) so the data layer
can be unit tested without installing SQLAlchemy or any ORM. This is
the local-development default described in the product spec; a
PostgreSQL-backed implementation behind the same function signatures
can be swapped in for production without touching the API routes.
"""
from __future__ import annotations

import datetime
import json
import sqlite3
import uuid
from contextlib import contextmanager
from typing import Any, Optional


SCHEMA = """
CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    owner TEXT NOT NULL,
    created_at TEXT NOT NULL,
    zip_filename TEXT,
    zip_size_bytes INTEGER,
    analysis_report TEXT,
    analyzed_at TEXT
);
"""


def connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    conn.commit()


@contextmanager
def cursor(conn: sqlite3.Connection):
    cur = conn.cursor()
    try:
        yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()


def create_project(conn: sqlite3.Connection, name: str, owner: str) -> dict:
    project_id = str(uuid.uuid4())
    created_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with cursor(conn) as cur:
        cur.execute(
            "INSERT INTO projects (id, name, owner, created_at) VALUES (?, ?, ?, ?)",
            (project_id, name, owner, created_at),
        )
    return get_project(conn, project_id)


def get_project(conn: sqlite3.Connection, project_id: str) -> Optional[dict]:
    row = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    if row is None:
        return None
    return _row_to_dict(row)


def list_projects(conn: sqlite3.Connection, owner: Optional[str] = None) -> list:
    if owner:
        rows = conn.execute(
            "SELECT * FROM projects WHERE owner = ? ORDER BY created_at DESC", (owner,)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM projects ORDER BY created_at DESC").fetchall()
    return [_row_to_dict(r) for r in rows]


def set_upload_metadata(
    conn: sqlite3.Connection, project_id: str, zip_filename: str, zip_size_bytes: int
) -> Optional[dict]:
    with cursor(conn) as cur:
        cur.execute(
            "UPDATE projects SET zip_filename = ?, zip_size_bytes = ? WHERE id = ?",
            (zip_filename, zip_size_bytes, project_id),
        )
    return get_project(conn, project_id)


def set_analysis_report(
    conn: sqlite3.Connection, project_id: str, report: dict
) -> Optional[dict]:
    analyzed_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with cursor(conn) as cur:
        cur.execute(
            "UPDATE projects SET analysis_report = ?, analyzed_at = ? WHERE id = ?",
            (json.dumps(report), analyzed_at, project_id),
        )
    return get_project(conn, project_id)


def _row_to_dict(row: sqlite3.Row) -> dict:
    d: dict[str, Any] = dict(row)
    if d.get("analysis_report"):
        d["analysis_report"] = json.loads(d["analysis_report"])
    return d
