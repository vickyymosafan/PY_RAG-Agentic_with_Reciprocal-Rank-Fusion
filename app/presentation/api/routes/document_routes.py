"""Document Routes."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.application.dto.document_dto import (
    DocumentListResponse,
    DocumentResponse,
    DocumentUploadRequest,
)
from app.presentation.api.dependencies import DocumentRepoDep, IngestUseCaseDep
from app.presentation.api.schemas import APIResponse

router = APIRouter(prefix="/api/documents", tags=["Documents"])


@router.post("", response_model=APIResponse[DocumentResponse])
async def upload_document(
    request: DocumentUploadRequest, ingest_use_case: IngestUseCaseDep
) -> APIResponse[DocumentResponse]:
    try:
        document, chunk_count = await ingest_use_case.execute(
            filename=request.filename, content=request.content
        )
        return APIResponse(
            success=True,
            data=DocumentResponse(
                id=str(document.id),
                filename=document.filename,
                chunk_count=chunk_count,
                metadata=document.metadata,
                created_at=document.created_at,
            ),
            message=f"Dokumen berhasil diupload dengan {chunk_count} chunks",
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("", response_model=APIResponse[DocumentListResponse])
async def list_documents(
    doc_repo: DocumentRepoDep, limit: int = 20, offset: int = 0
) -> APIResponse[DocumentListResponse]:
    documents = await doc_repo.get_all(limit=limit, offset=offset)
    doc_responses = [
        DocumentResponse(
            id=str(doc.id),
            filename=doc.filename,
            chunk_count=0,
            metadata=doc.metadata,
            created_at=doc.created_at,
        )
        for doc in documents
    ]
    return APIResponse(
        success=True,
        data=DocumentListResponse(documents=doc_responses, total=len(doc_responses)),
    )


@router.delete("/{document_id}")
async def delete_document(document_id: str, doc_repo: DocumentRepoDep) -> APIResponse:
    try:
        deleted = await doc_repo.delete(UUID(document_id))
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
        return APIResponse(success=True, message="Dokumen berhasil dihapus")
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID")
