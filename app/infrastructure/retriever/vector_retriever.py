"""Vector Retriever Implementation."""

from app.domain.interfaces.chunk_repository import IChunkRepository
from app.domain.interfaces.embedding_service import IEmbeddingService
from app.domain.interfaces.retriever_service import IRetrieverService, RetrievalResult


class VectorRetriever(IRetrieverService):
    def __init__(
        self,
        chunk_repository: IChunkRepository,
        embedding_service: IEmbeddingService,
    ) -> None:
        self._chunk_repo = chunk_repository
        self._embedding_service = embedding_service

    async def retrieve(self, query: str, top_k: int = 5) -> list[RetrievalResult]:
        if hasattr(self._embedding_service, "embed_query"):
            query_embedding = await self._embedding_service.embed_query(query)
        else:
            query_embedding = await self._embedding_service.embed_text(query)

        results = await self._chunk_repo.search_by_embedding(
            embedding=query_embedding, top_k=top_k
        )

        return [
            RetrievalResult(chunk=chunk, score=score, source="vector")
            for chunk, score in results
        ]
