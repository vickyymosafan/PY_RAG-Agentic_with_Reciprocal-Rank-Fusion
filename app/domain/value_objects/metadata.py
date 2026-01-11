"""DocumentMetadata value object."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    """Value object untuk metadata dokumen."""

    source: str
    title: str | None = None
    description: str | None = None
    uploaded_at: datetime = Field(default_factory=datetime.now)
    extra: dict[str, Any] = Field(default_factory=dict)

    class Config:
        frozen = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "title": self.title,
            "description": self.description,
            "uploaded_at": self.uploaded_at.isoformat(),
            **self.extra,
        }
