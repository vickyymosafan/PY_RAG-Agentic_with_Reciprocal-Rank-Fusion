"""
ChatMessage entity - Represents a message in chat history.
"""

from datetime import datetime
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """ChatMessage entity mewakili pesan dalam chat history."""

    id: UUID = Field(default_factory=uuid4)
    session_id: str
    role: Literal["user", "assistant", "system"]
    content: str
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True

    def to_dict(self) -> dict:
        return {"role": self.role, "content": self.content}
