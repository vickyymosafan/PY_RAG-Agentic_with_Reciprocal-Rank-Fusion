"""
Document entity - Represents an uploaded document.
"""

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Document(BaseModel):
    """Document entity mewakili dokumen yang diupload."""

    id: UUID = Field(default_factory=uuid4)
    filename: str
    content_hash: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True
