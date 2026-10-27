"""
Project endpoints: create, list, upload a source ZIP, and analyze it.

This is the minimal end-to-end slice: every response here is backed by
a real SQLite row and, for /analyze, a real run of the stdlib ZIP
analyzer in app.services.zip_analyzer — nothing here is mocked.
"""
from __future__ import annotations

import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, status

from app import database
from app.config import settings
from app.security import require_api_key
from app.services import storage
from app.services.zip_analyzer import analyze_zip_bytes
from app.schemas import AnalysisResult, ProjectCreate, ProjectOut, UploadResult

router = APIRouter(prefix="/api/v1/projects", tags=["projects"])


def get_db(request: Request) -> sqlite3.Connection:
    return request.app.state.db


@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
async def create_project(
    body: ProjectCreate,
    owner: str = Depends(require_api_key),
    db: sqlite3.Connection = Depends(get_db),
) -> ProjectOut:
    project = database.create_project(db, name=body.name, owner=owner)
    return ProjectOut(**project)


@router.get("", response_model=list[ProjectOut])
async def list_projects(
    owner: str = Depends(require_api_key),
    db: sqlite3.Connection = Depends(get_db),
) -> list[ProjectOut]:
    projects = database.list_projects(db, owner=owner)
    return [ProjectOut(**p) for p in projects]


@router.get("/{project_id}", response_model=ProjectOut)
async def get_project(
    project_id: str,
    owner: str = Depends(require_api_key),
    db: sqlite3.Connection = Depends(get_db),
) -> ProjectOut:
    project = database.get_project(db, project_id)
    if project is None or project["owner"] != owner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
    return ProjectOut(**project)


@router.post("/{project_id}/upload", response_model=UploadResult)
async def upload_project_zip(
    project_id: str,
    file: UploadFile,
    owner: str = Depends(require_api_key),
    db: sqlite3.Connection = Depends(get_db),
) -> UploadResult:
    project = database.get_project(db, project_id)
    if project is None or project["owner"] != owner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    if file.filename and not file.filename.lower().endswith(".zip"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .zip files are accepted.",
        )

    # Read in bounded chunks so an oversized upload is rejected before
    # it is fully buffered in memory.
    chunks = []
    total = 0
    chunk_size = 1024 * 1024
    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        total += len(chunk)
        if total > settings.max_upload_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=(
                    f"Upload exceeds the {settings.max_upload_size_bytes} byte limit."
                ),
            )
        chunks.append(chunk)
    data = b"".join(chunks)

    if not data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file upload.")

    storage.save_zip(settings.storage_dir, project_id, data)
    updated = database.set_upload_metadata(
        db, project_id, zip_filename=file.filename or "upload.zip", zip_size_bytes=len(data)
    )
    return UploadResult(project=ProjectOut(**updated), message="Upload received.")


@router.post("/{project_id}/analyze", response_model=AnalysisResult)
async def analyze_project(
    project_id: str,
    owner: str = Depends(require_api_key),
    db: sqlite3.Connection = Depends(get_db),
) -> AnalysisResult:
    project = database.get_project(db, project_id)
    if project is None or project["owner"] != owner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    if not storage.zip_exists(settings.storage_dir, project_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No archive uploaded for this project yet. Call /upload first.",
        )

    data = storage.load_zip(settings.storage_dir, project_id)
    report = analyze_zip_bytes(
        data,
        max_entries=settings.max_zip_entries,
        max_uncompressed_bytes=settings.max_uncompressed_size_bytes,
    )
    report_dict = report.to_dict()
    updated = database.set_analysis_report(db, project_id, report_dict)
    return AnalysisResult(project=ProjectOut(**updated), report=report_dict)
