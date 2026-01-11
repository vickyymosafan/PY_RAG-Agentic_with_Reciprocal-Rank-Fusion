"""FastAPI Dependencies."""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Cookie, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.orchestrators.rag_pipeline import RAGPipeline
from app.application.use_cases.chat_with_rag import ChatWithRAGUseCase
from app.application.use_cases.ingest_document import IngestDocumentUseCase
from app.config import Settings, get_settings
from app.domain.interfaces.cache_service import ICacheService
from app.domain.interfaces.chunk_repository import IChunkRepository
from app.domain.interfaces.document_repository import IDocumentRepository
from app.domain.interfaces.embedding_service import IEmbeddingService
from app.domain.interfaces.llm_service import ILLMService
from app.infrastructure.cache.redis_cache import RedisCacheService
from app.infrastructure.database.connection import get_db_session
from app.infrastructure.database.repositories.chunk_repo import PostgresChunkRepository
from app.infrastructure.database.repositories.document_repo import PostgresDocumentRepository
from app.infrastructure.embedding.cohere_embedding import CohereEmbeddingService
from app.infrastructure.llm.cohere_llm import CohereLLMService


def get_app_settings() -> Settings:
    return get_settings()


SettingsDep = Annotated[Settings, Depends(get_app_settings)]


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with get_db_session() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def get_document_repository(session: SessionDep) -> IDocumentRepository:
    return PostgresDocumentRepository(session)


async def get_chunk_repository(session: SessionDep) -> IChunkRepository:
    return PostgresChunkRepository(session)


DocumentRepoDep = Annotated[IDocumentRepository, Depends(get_document_repository)]
ChunkRepoDep = Annotated[IChunkRepository, Depends(get_chunk_repository)]

_cache_service: RedisCacheService | None = None


async def get_cache_service() -> ICacheService:
    global _cache_service
    if _cache_service is None:
        _cache_service = RedisCacheService()
    return _cache_service


_embedding_service: CohereEmbeddingService | None = None


async def get_embedding_service() -> IEmbeddingService:
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = CohereEmbeddingService()
    return _embedding_service


_llm_service: CohereLLMService | None = None


async def get_llm_service() -> ILLMService:
    global _llm_service
    if _llm_service is None:
        _llm_service = CohereLLMService()
    return _llm_service


CacheServiceDep = Annotated[ICacheService, Depends(get_cache_service)]
EmbeddingServiceDep = Annotated[IEmbeddingService, Depends(get_embedding_service)]
LLMServiceDep = Annotated[ILLMService, Depends(get_llm_service)]


async def get_ingest_use_case(
    doc_repo: DocumentRepoDep,
    chunk_repo: ChunkRepoDep,
    embedding_service: EmbeddingServiceDep,
) -> IngestDocumentUseCase:
    return IngestDocumentUseCase(
        document_repo=doc_repo,
        chunk_repo=chunk_repo,
        embedding_service=embedding_service,
    )


async def get_chat_use_case(
    chunk_repo: ChunkRepoDep,
    embedding_service: EmbeddingServiceDep,
    llm_service: LLMServiceDep,
    cache_service: CacheServiceDep,
    settings: SettingsDep,
) -> ChatWithRAGUseCase:
    pipeline = RAGPipeline(
        chunk_repository=chunk_repo,
        embedding_service=embedding_service,
        llm_service=llm_service,
        cache_service=cache_service,
        rrf_k=settings.rrf_k,
    )
    await pipeline.initialize()
    return ChatWithRAGUseCase(
        retriever=pipeline._hybrid,
        llm_service=llm_service,
        cache_service=cache_service,
    )


IngestUseCaseDep = Annotated[IngestDocumentUseCase, Depends(get_ingest_use_case)]
ChatUseCaseDep = Annotated[ChatWithRAGUseCase, Depends(get_chat_use_case)]


def get_session_id(session_id: Annotated[str | None, Cookie()] = None) -> str | None:
    return session_id


SessionIdDep = Annotated[str | None, Depends(get_session_id)]
