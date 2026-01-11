"""Retrieval DTOs."""

from pydantic import BaseModel, Field


class RetrievalRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query")
    top_k: int = Field(5, ge=1, le=20)


class ChunkResult(BaseModel):
    id: str
    content: str
    score: float
    source: str
    document_id: str


class RetrievalResponse(BaseModel):
    query: str
    results: list[ChunkResult]
    total: int
