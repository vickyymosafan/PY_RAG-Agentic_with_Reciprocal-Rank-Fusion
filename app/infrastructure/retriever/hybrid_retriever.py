"""Hybrid Retriever Implementation with RRF fusion."""

from app.domain.interfaces.retriever_service import IRetrieverService, RetrievalResult


class HybridRetriever(IRetrieverService):
    def __init__(
        self,
        bm25_retriever: IRetrieverService,
        vector_retriever: IRetrieverService,
        rrf_k: int = 60,
    ) -> None:
        self._bm25 = bm25_retriever
        self._vector = vector_retriever
        self._rrf_k = rrf_k

    async def retrieve(self, query: str, top_k: int = 5) -> list[RetrievalResult]:
        fetch_k = top_k * 2
        bm25_results = await self._bm25.retrieve(query, fetch_k)
        vector_results = await self._vector.retrieve(query, fetch_k)
        fused_results = self._rrf_fusion(bm25_results, vector_results)

        sorted_results = sorted(fused_results.values(), key=lambda x: x.score, reverse=True)
        return sorted_results[:top_k]

    def _rrf_fusion(
        self,
        bm25_results: list[RetrievalResult],
        vector_results: list[RetrievalResult],
    ) -> dict[str, RetrievalResult]:
        fused: dict[str, RetrievalResult] = {}

        for rank, result in enumerate(bm25_results, start=1):
            chunk_id = str(result.chunk.id)
            rrf_score = 1 / (self._rrf_k + rank)

            if chunk_id in fused:
                fused[chunk_id] = RetrievalResult(
                    chunk=result.chunk,
                    score=fused[chunk_id].score + rrf_score,
                    source="hybrid",
                )
            else:
                fused[chunk_id] = RetrievalResult(
                    chunk=result.chunk, score=rrf_score, source="hybrid"
                )

        for rank, result in enumerate(vector_results, start=1):
            chunk_id = str(result.chunk.id)
            rrf_score = 1 / (self._rrf_k + rank)

            if chunk_id in fused:
                fused[chunk_id] = RetrievalResult(
                    chunk=fused[chunk_id].chunk,
                    score=fused[chunk_id].score + rrf_score,
                    source="hybrid",
                )
            else:
                fused[chunk_id] = RetrievalResult(
                    chunk=result.chunk, score=rrf_score, source="hybrid"
                )

        return fused
