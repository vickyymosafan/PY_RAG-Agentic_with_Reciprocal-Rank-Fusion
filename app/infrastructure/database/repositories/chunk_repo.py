"""Chunk Repository Implementation."""

from uuid import UUID

from sqlalchemy import delete, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.chunk import Chunk
from app.domain.interfaces.chunk_repository import IChunkRepository
from app.infrastructure.database.models import ChunkModel


class PostgresChunkRepository(IChunkRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, chunk: Chunk) -> Chunk:
        db_model = self._to_model(chunk)
        self._session.add(db_model)
        await self._session.flush()
        return chunk

    async def save_many(self, chunks: list[Chunk]) -> list[Chunk]:
        db_models = [self._to_model(c) for c in chunks]
        self._session.add_all(db_models)
        await self._session.flush()
        return chunks

    async def get_by_document_id(self, document_id: UUID) -> list[Chunk]:
        stmt = (
            select(ChunkModel)
            .where(ChunkModel.document_id == str(document_id))
            .order_by(ChunkModel.chunk_index)
        )
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_all(self, limit: int = 1000) -> list[Chunk]:
        stmt = select(ChunkModel).limit(limit)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def search_by_embedding(
        self, embedding: list[float], top_k: int = 5
    ) -> list[tuple[Chunk, float]]:
        embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"
        query = text("""
            SELECT id, document_id, content, chunk_index, content_hash,
                   embedding, metadata, created_at,
                   1 - (embedding <=> :embedding::vector) as similarity
            FROM chunks WHERE embedding IS NOT NULL
            ORDER BY embedding <=> :embedding::vector LIMIT :top_k
        """)
        result = await self._session.execute(
            query, {"embedding": embedding_str, "top_k": top_k}
        )
        results = []
        for row in result.fetchall():
            chunk = Chunk(
                id=UUID(row.id),
                document_id=UUID(row.document_id),
                content=row.content,
                chunk_index=row.chunk_index,
                content_hash=row.content_hash,
                embedding=list(row.embedding) if row.embedding else None,
                metadata=row.metadata,
                created_at=row.created_at,
            )
            results.append((chunk, float(row.similarity)))
        return results

    async def get_by_hash(self, content_hash: str) -> Chunk | None:
        stmt = select(ChunkModel).where(ChunkModel.content_hash == content_hash)
        result = await self._session.execute(stmt)
        db_model = result.scalar_one_or_none()
        return self._to_entity(db_model) if db_model else None

    async def delete_by_document_id(self, document_id: UUID) -> int:
        stmt = delete(ChunkModel).where(ChunkModel.document_id == str(document_id))
        result = await self._session.execute(stmt)
        return result.rowcount

    def _to_model(self, entity: Chunk) -> ChunkModel:
        return ChunkModel(
            id=str(entity.id),
            document_id=str(entity.document_id),
            content=entity.content,
            chunk_index=entity.chunk_index,
            content_hash=entity.content_hash,
            embedding=entity.embedding,
            metadata_=entity.metadata,
            created_at=entity.created_at,
        )

    def _to_entity(self, model: ChunkModel) -> Chunk:
        return Chunk(
            id=UUID(model.id),
            document_id=UUID(model.document_id),
            content=model.content,
            chunk_index=model.chunk_index,
            content_hash=model.content_hash,
            embedding=list(model.embedding) if model.embedding else None,
            metadata=model.metadata_,
            created_at=model.created_at,
        )
