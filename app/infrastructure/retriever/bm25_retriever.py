"""BM25 Retriever Implementation."""

from rank_bm25 import BM25Okapi

from app.domain.entities.chunk import Chunk
from app.domain.interfaces.retriever_service import IRetrieverService, RetrievalResult


class BM25Retriever(IRetrieverService):
    def __init__(self, chunks: list[Chunk] | None = None) -> None:
        self._chunks: list[Chunk] = []
        self._bm25: BM25Okapi | None = None
        self._tokenized_corpus: list[list[str]] = []
        if chunks:
            self.build_index(chunks)

    def build_index(self, chunks: list[Chunk]) -> None:
        self._chunks = chunks
        self._tokenized_corpus = [self._tokenize(c.content) for c in chunks]
        if self._tokenized_corpus:
            self._bm25 = BM25Okapi(self._tokenized_corpus)

    def _tokenize(self, text: str) -> list[str]:
        text = text.lower()
        words = text.split()
        return [w for w in words if len(w) > 1]

    async def retrieve(self, query: str, top_k: int = 5) -> list[RetrievalResult]:
        if self._bm25 is None or not self._chunks:
            return []

        tokenized_query = self._tokenize(query)
        if not tokenized_query:
            return []

        scores = self._bm25.get_scores(tokenized_query)
        scored_indices = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:top_k]

        results = []
        for idx, score in scored_indices:
            if score > 0:
                results.append(
                    RetrievalResult(chunk=self._chunks[idx], score=float(score), source="bm25")
                )
        return results
