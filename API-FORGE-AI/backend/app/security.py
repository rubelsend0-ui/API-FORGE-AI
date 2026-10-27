"""
Minimal API-key authentication dependency.

This is an intentionally simple MVP auth mechanism: a single shared
key checked via constant-time comparison. It is enough to keep the
backend from being an open, unauthenticated service while the project
is local-only. Before deploying multi-user, replace this with real
per-user auth (e.g. GitHub OAuth-backed sessions) — see
docs/BACKEND_SETUP.md.
"""
from __future__ import annotations

import hmac

from fastapi import Header, HTTPException, status

from app.config import settings


async def require_api_key(x_api_key: str = Header(default="")) -> str:
    if not x_api_key or not hmac.compare_digest(x_api_key, settings.app_secret_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid X-API-Key header.",
        )
    # In this MVP, the key itself stands in for the "owner" identity.
    # Swap this for a real user id once per-user auth is implemented.
    return "default-owner"
