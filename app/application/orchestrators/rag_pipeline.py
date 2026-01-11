"""RAG Pipeline Orchestrator."""

from collections.abc import AsyncGenerator

from app.domain.interfaces.cache_service import ICacheService
from app.domain.interfaces.chunk_repository import IChunkRepository
from app.domain.interfaces.embedding_service import IEmbeddingService
from app.domain.interfaces.llm_service import ILLMService
from app.domain.interfaces.retriever_service import RetrievalResult
from app.infrastructure.retriever.bm25_retriever import BM25Retriever
from app.infrastructure.retriever.hybrid_retriever import HybridRetriever
from app.infrastructure.retriever.vector_retriever import VectorRetriever


class RAGPipeline:
    def __init__(
        self,
        chunk_repository: IChunkRepository,
        embedding_service: IEmbeddingService,
        llm_service: ILLMService,
        cache_service: ICacheService,
        rrf_k: int = 60,
    ) -> None:
        self._chunk_repo = chunk_repository
        self._embedding_service = embedding_service
        self._llm = llm_service
        self._cache = cache_service
        self._rrf_k = rrf_k
        self._bm25: BM25Retriever | None = None
        self._vector: VectorRetriever | None = None
        self._hybrid: HybridRetriever | None = None

    async def initialize(self) -> None:
        chunks = await self._chunk_repo.get_all()
        self._bm25 = BM25Retriever(chunks)
        self._vector = VectorRetriever(
            chunk_repository=self._chunk_repo,
            embedding_service=self._embedding_service,
        )
        self._hybrid = HybridRetriever(
            bm25_retriever=self._bm25,
            vector_retriever=self._vector,
            rrf_k=self._rrf_k,
        )

    async def retrieve(self, query: str, top_k: int = 5) -> list[RetrievalResult]:
        if self._hybrid is None:
            await self.initialize()
        return await self._hybrid.retrieve(query, top_k)

    async def generate(
        self, query: str, top_k: int = 5, chat_history: list[dict] | None = None
    ) -> tuple[str, list[RetrievalResult]]:
        results = await self.retrieve(query, top_k)
        context = self._build_context(results)
        response = await self._llm.generate(
            prompt=query, context=context, chat_history=chat_history
        )
        return response, results

    def _build_context(self, results: list[RetrievalResult]) -> str | None:
        if not results:
            return None
        parts = [f"[Sumber {i}]\n{r.chunk.content}" for i, r in enumerate(results, 1)]
        return "\n\n---\n\n".join(parts)
