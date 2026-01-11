"""Chat DTOs."""

from datetime import datetime
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Pesan dari user")
    session_id: str | None = Field(None, description="Session ID untuk history")


class ChatResponse(BaseModel):
    message: str
    session_id: str
    sources: list[str] = Field(default_factory=list)
    cached: bool = False


class ChatHistoryItem(BaseModel):
    role: str
    content: str
    created_at: datetime


class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: list[ChatHistoryItem]
