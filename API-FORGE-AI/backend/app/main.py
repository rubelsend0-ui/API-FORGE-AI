"""
API Forge AI backend entrypoint.

Run locally:
    uvicorn app.main:app --reload --port 8000

This MVP slice wires up:
  - GET  /health
  - POST /api/v1/projects
  - GET  /api/v1/projects
  - GET  /api/v1/projects/{id}
  - POST /api/v1/projects/{id}/upload
  - POST /api/v1/projects/{id}/analyze

Everything else described in the full product spec (GitHub integration,
Render deployment, API generation/build workers, auth beyond a shared
API key) is NOT implemented yet. Those routes are intentionally absent
rather than faked — see docs/BACKEND_SETUP.md for what's next.
"""
from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import database
from app.api import health, projects
from app.config import settings

app = FastAPI(
    title=settings.app_name,
    description="Minimal, honest MVP backend for API Forge AI.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(projects.router)


@app.on_event("startup")
async def on_startup() -> None:
    os.makedirs(os.path.dirname(settings.database_path) or ".", exist_ok=True)
    os.makedirs(settings.storage_dir, exist_ok=True)
    conn = database.connect(settings.database_path)
    database.init_db(conn)
    app.state.db = conn


@app.on_event("shutdown")
async def on_shutdown() -> None:
    db = getattr(app.state, "db", None)
    if db is not None:
        db.close()
