"""Document Repository Interface."""

from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.document import Document


class IDocumentRepository(ABC):
    """Interface untuk Document Repository."""

    @abstractmethod
    async def save(self, document: Document) -> Document:
        pass

    @abstractmethod
    async def get_by_id(self, document_id: UUID) -> Document | None:
        pass

    @abstractmethod
    async def get_by_hash(self, content_hash: str) -> Document | None:
        pass

    @abstractmethod
    async def get_all(self, limit: int = 100, offset: int = 0) -> list[Document]:
        pass

    @abstractmethod
    async def delete(self, document_id: UUID) -> bool:
        pass
