"""Chat Routes."""

from fastapi import APIRouter, HTTPException, Response, status

from app.application.dto.chat_dto import ChatRequest, ChatResponse
from app.presentation.api.dependencies import CacheServiceDep, ChatUseCaseDep, SessionIdDep
from app.presentation.api.schemas import APIResponse

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("", response_model=APIResponse[ChatResponse])
async def chat(
    request: ChatRequest,
    chat_use_case: ChatUseCaseDep,
    session_id: SessionIdDep,
    response: Response,
) -> APIResponse[ChatResponse]:
    try:
        sid = request.session_id or session_id
        result, new_session_id, sources, cached = await chat_use_case.execute(
            message=request.message, session_id=sid
        )
        response.set_cookie(key="session_id", value=new_session_id, httponly=True, max_age=86400)
        return APIResponse(
            success=True,
            data=ChatResponse(
                message=result, session_id=new_session_id, sources=sources, cached=cached
            ),
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/history")
async def get_chat_history(
    cache_service: CacheServiceDep, session_id: SessionIdDep
) -> APIResponse:
    if not session_id:
        return APIResponse(success=True, data={"messages": []})

    history = await cache_service.get_chat_history(session_id)
    messages = [
        {"role": msg.role, "content": msg.content, "created_at": msg.created_at.isoformat()}
        for msg in history
    ]
    return APIResponse(success=True, data={"session_id": session_id, "messages": messages})


@router.delete("/history")
async def clear_chat_history(
    cache_service: CacheServiceDep, session_id: SessionIdDep
) -> APIResponse:
    if session_id:
        await cache_service.clear_chat_history(session_id)
    return APIResponse(success=True, message="Chat history cleared")
