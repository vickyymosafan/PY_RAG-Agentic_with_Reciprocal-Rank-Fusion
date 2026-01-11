"""Retriever Service Interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.domain.entities.chunk import Chunk


@dataclass
class RetrievalResult:
    """Result dari retrieval dengan score."""
    chunk: Chunk
    score: float
    source: str  # "bm25", "vector", atau "hybrid"


class IRetrieverService(ABC):
    """Interface untuk Retriever Service."""

    @abstractmethod
    async def retrieve(self, query: str, top_k: int = 5) -> list[RetrievalResult]:
        pass
