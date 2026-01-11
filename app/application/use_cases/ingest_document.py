"""Ingest Document Use Case."""

import hashlib
import json
from typing import Any
from uuid import uuid4

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import get_settings
from app.domain.entities.chunk import Chunk
from app.domain.entities.document import Document
from app.domain.interfaces.chunk_repository import IChunkRepository
from app.domain.interfaces.document_repository import IDocumentRepository
from app.domain.interfaces.embedding_service import IEmbeddingService


class IngestDocumentUseCase:
    def __init__(
        self,
        document_repo: IDocumentRepository,
        chunk_repo: IChunkRepository,
        embedding_service: IEmbeddingService,
    ) -> None:
        self._doc_repo = document_repo
        self._chunk_repo = chunk_repo
        self._embedding_service = embedding_service
        self._settings = get_settings()
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=self._settings.chunk_size,
            chunk_overlap=self._settings.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    async def execute(
        self, filename: str, content: list[dict[str, Any]]
    ) -> tuple[Document, int]:
        texts = self._extract_texts(content)
        combined_text = "\n\n".join(texts)
        content_hash = self._generate_hash(combined_text)

        existing = await self._doc_repo.get_by_hash(content_hash)
        if existing:
            chunks = await self._chunk_repo.get_by_document_id(existing.id)
            return existing, len(chunks)

        document = Document(
            id=uuid4(),
            filename=filename,
            content_hash=content_hash,
            metadata={"source": filename, "item_count": len(content)},
        )

        chunk_texts = self._splitter.split_text(combined_text)
        embeddings = await self._embedding_service.embed_texts(chunk_texts)

        chunks = []
        for idx, (text, embedding) in enumerate(zip(chunk_texts, embeddings)):
            chunk_hash = self._generate_hash(text)
            existing_chunk = await self._chunk_repo.get_by_hash(chunk_hash)
            if existing_chunk:
                continue

            chunk = Chunk(
                id=uuid4(),
                document_id=document.id,
                content=text,
                chunk_index=idx,
                content_hash=chunk_hash,
                embedding=embedding,
                metadata={"document_filename": filename, "chunk_index": idx},
            )
            chunks.append(chunk)

        await self._doc_repo.save(document)
        if chunks:
            await self._chunk_repo.save_many(chunks)

        return document, len(chunks)

    def _extract_texts(self, content: list[dict[str, Any]]) -> list[str]:
        texts = []
        text_fields = ["content", "text", "body", "description", "title"]

        for item in content:
            item_texts = []
            for field in text_fields:
                if field in item and isinstance(item[field], str):
                    item_texts.append(item[field])

            if item_texts:
                texts.append(" ".join(item_texts))
            else:
                texts.append(json.dumps(item, ensure_ascii=False))

        return texts

    def _generate_hash(self, text: str) -> str:
        return hashlib.md5(text.encode()).hexdigest()
