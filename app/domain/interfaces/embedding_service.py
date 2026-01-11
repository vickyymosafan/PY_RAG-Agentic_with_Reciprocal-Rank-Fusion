"""Embedding Service Interface."""

from abc import ABC, abstractmethod


class IEmbeddingService(ABC):
    """Interface untuk Embedding Service."""

    @abstractmethod
    async def embed_text(self, text: str) -> list[float]:
        pass

    @abstractmethod
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        pass

    @property
    @abstractmethod
    def embedding_dimension(self) -> int:
        pass
