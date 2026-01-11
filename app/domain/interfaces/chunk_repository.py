"""Chunk Repository Interface."""

from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.chunk import Chunk


class IChunkRepository(ABC):
    """Interface untuk Chunk Repository."""

    @abstractmethod
    async def save(self, chunk: Chunk) -> Chunk:
        pass

    @abstractmethod
    async def save_many(self, chunks: list[Chunk]) -> list[Chunk]:
        pass

    @abstractmethod
    async def get_by_document_id(self, document_id: UUID) -> list[Chunk]:
        pass

    @abstractmethod
    async def get_all(self, limit: int = 1000) -> list[Chunk]:
        pass

    @abstractmethod
    async def search_by_embedding(
        self, embedding: list[float], top_k: int = 5
    ) -> list[tuple[Chunk, float]]:
        pass

    @abstractmethod
    async def get_by_hash(self, content_hash: str) -> Chunk | None:
        pass

    @abstractmethod
    async def delete_by_document_id(self, document_id: UUID) -> int:
        pass
