"""Document Repository Implementation."""

from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.document import Document
from app.domain.interfaces.document_repository import IDocumentRepository
from app.infrastructure.database.models import DocumentModel


class PostgresDocumentRepository(IDocumentRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, document: Document) -> Document:
        db_model = DocumentModel(
            id=str(document.id),
            filename=document.filename,
            content_hash=document.content_hash,
            metadata_=document.metadata,
            created_at=document.created_at,
            updated_at=document.updated_at,
        )
        self._session.add(db_model)
        await self._session.flush()
        return document

    async def get_by_id(self, document_id: UUID) -> Document | None:
        stmt = select(DocumentModel).where(DocumentModel.id == str(document_id))
        result = await self._session.execute(stmt)
        db_model = result.scalar_one_or_none()
        return self._to_entity(db_model) if db_model else None

    async def get_by_hash(self, content_hash: str) -> Document | None:
        stmt = select(DocumentModel).where(DocumentModel.content_hash == content_hash)
        result = await self._session.execute(stmt)
        db_model = result.scalar_one_or_none()
        return self._to_entity(db_model) if db_model else None

    async def get_all(self, limit: int = 100, offset: int = 0) -> list[Document]:
        stmt = (
            select(DocumentModel)
            .order_by(DocumentModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def delete(self, document_id: UUID) -> bool:
        stmt = delete(DocumentModel).where(DocumentModel.id == str(document_id))
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    def _to_entity(self, model: DocumentModel) -> Document:
        return Document(
            id=UUID(model.id),
            filename=model.filename,
            content_hash=model.content_hash,
            metadata=model.metadata_,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
