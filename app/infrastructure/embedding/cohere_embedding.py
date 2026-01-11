"""Cohere Embedding Service Implementation."""

import cohere

from app.config import get_settings
from app.domain.interfaces.embedding_service import IEmbeddingService


class CohereEmbeddingService(IEmbeddingService):
    MODEL_DIMENSIONS = {
        "embed-multilingual-v3.0": 1024,
        "embed-english-v3.0": 1024,
        "embed-multilingual-light-v3.0": 384,
        "embed-english-light-v3.0": 384,
    }

    def __init__(self, client: cohere.ClientV2 | None = None) -> None:
        self._settings = get_settings()
        self._client = client or cohere.ClientV2(api_key=self._settings.cohere_api_key)
        self._model = self._settings.embedding_model

    @property
    def embedding_dimension(self) -> int:
        return self.MODEL_DIMENSIONS.get(self._model, 1024)

    async def embed_text(self, text: str) -> list[float]:
        embeddings = await self.embed_texts([text])
        return embeddings[0]

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        response = self._client.embed(
            texts=texts,
            model=self._model,
            input_type="search_document",
            embedding_types=["float"],
        )
        return response.embeddings.float_

    async def embed_query(self, query: str) -> list[float]:
        response = self._client.embed(
            texts=[query],
            model=self._model,
            input_type="search_query",
            embedding_types=["float"],
        )
        return response.embeddings.float_[0]
