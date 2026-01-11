"""
Chunk entity - Represents a text chunk from a document.
"""

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Chunk(BaseModel):
    """Chunk entity mewakili potongan teks dari dokumen."""

    id: UUID = Field(default_factory=uuid4)
    document_id: UUID
    content: str
    chunk_index: int
    content_hash: str
    embedding: list[float] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True

    @property
    def has_embedding(self) -> bool:
        return self.embedding is not None and len(self.embedding) > 0
