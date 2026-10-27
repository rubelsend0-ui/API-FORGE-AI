"""Pydantic request/response schemas."""
from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)


class ProjectOut(BaseModel):
    id: str
    name: str
    owner: str
    created_at: str
    zip_filename: Optional[str] = None
    zip_size_bytes: Optional[int] = None
    analysis_report: Optional[dict[str, Any]] = None
    analyzed_at: Optional[str] = None


class UploadResult(BaseModel):
    project: ProjectOut
    message: str


class AnalysisResult(BaseModel):
    project: ProjectOut
    report: dict[str, Any]


class HealthOut(BaseModel):
    status: str
    service: str
    environment: str


class ErrorOut(BaseModel):
    detail: str
