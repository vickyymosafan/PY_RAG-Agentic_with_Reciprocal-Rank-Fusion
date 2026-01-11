"""Document DTOs."""

from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class DocumentUploadRequest(BaseModel):
    filename: str = Field(..., description="Nama file")
    content: list[dict[str, Any]] = Field(..., description="Konten JSON array")


class DocumentResponse(BaseModel):
    id: str
    filename: str
    chunk_count: int
    metadata: dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]
    total: int
