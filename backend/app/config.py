"""
Centralized, environment-driven configuration.

Nothing here has a real secret baked in — every sensitive value comes
from an environment variable with a clearly-fake local-dev default.
See backend/.env.example for the full list of variables.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field


def _get_bool(name: str, default: bool) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


def _get_list(name: str, default: list) -> list:
    val = os.getenv(name)
    if not val:
        return default
    return [item.strip() for item in val.split(",") if item.strip()]


@dataclass
class Settings:
    app_name: str = "API Forge AI Backend"
    environment: str = os.getenv("ENVIRONMENT", "development")

    # Local SQLite by default. A Postgres DATABASE_URL can be swapped in
    # behind the same app.database function signatures for production.
    database_path: str = os.getenv("DATABASE_PATH", "./data/apiforge.db")

    # Shared API key for the MVP (single-tenant / internal use). This is
    # intentionally simple; see docs/BACKEND_SETUP.md for how to replace
    # it with per-user auth before exposing the backend publicly.
    app_secret_key: str = os.getenv("APP_SECRET_KEY", "dev-secret-change-me")

    storage_dir: str = os.getenv("STORAGE_DIR", "./data/uploads")

    max_upload_size_bytes: int = int(os.getenv("MAX_UPLOAD_SIZE_BYTES", str(50 * 1024 * 1024)))
    max_zip_entries: int = int(os.getenv("MAX_ZIP_ENTRIES", "2000"))
    max_uncompressed_size_bytes: int = int(
        os.getenv("MAX_UNCOMPRESSED_SIZE_BYTES", str(200 * 1024 * 1024))
    )

    cors_allow_origins: list = field(
        default_factory=lambda: _get_list("CORS_ALLOW_ORIGINS", ["http://localhost"])
    )

    public_base_url: str = os.getenv("PUBLIC_BASE_URL", "http://localhost:8000")

    # Optional integrations. Left unset until the user configures them;
    # every endpoint that depends on these must report a clear
    # "not configured" state rather than pretending to work.
    github_app_id: str = os.getenv("GITHUB_APP_ID", "")
    github_client_id: str = os.getenv("GITHUB_CLIENT_ID", "")
    github_client_secret: str = os.getenv("GITHUB_CLIENT_SECRET", "")
    github_webhook_secret: str = os.getenv("GITHUB_WEBHOOK_SECRET", "")
    render_api_key: str = os.getenv("RENDER_API_KEY", "")


settings = Settings()
