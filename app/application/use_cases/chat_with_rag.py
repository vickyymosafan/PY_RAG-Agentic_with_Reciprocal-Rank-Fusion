"""Chat with RAG Use Case."""

import hashlib
from uuid import uuid4

from app.config import get_settings
from app.domain.entities.chat_message import ChatMessage
from app.domain.interfaces.cache_service import ICacheService
from app.domain.interfaces.llm_service import ILLMService
from app.domain.interfaces.retriever_service import IRetrieverService


class ChatWithRAGUseCase:
    def __init__(
        self,
        retriever: IRetrieverService,
        llm_service: ILLMService,
        cache_service: ICacheService,
    ) -> None:
        self._retriever = retriever
        self._llm = llm_service
        self._cache = cache_service
        self._settings = get_settings()

    async def execute(
        self, message: str, session_id: str | None = None
    ) -> tuple[str, str, list[str], bool]:
        if not session_id:
            session_id = str(uuid4())

        cache_key = self._generate_cache_key(message)
        cached_response = await self._cache.get(cache_key)

        if cached_response:
            await self._save_messages(session_id, message, cached_response["response"])
            return (
                cached_response["response"],
                session_id,
                cached_response.get("sources", []),
                True,
            )

        history = await self._cache.get_chat_history(session_id, limit=10)
        chat_history = [msg.to_dict() for msg in history]

        results = await self._retriever.retrieve(
            query=message, top_k=self._settings.top_k
        )

        context_parts = []
        sources = []
        for result in results:
            context_parts.append(result.chunk.content)
            sources.append(f"Chunk {result.chunk.chunk_index}")

        context = "\n\n---\n\n".join(context_parts) if context_parts else None

        response = await self._llm.generate(
            prompt=message, context=context, chat_history=chat_history
        )

        await self._cache.set(
            cache_key,
            {"response": response, "sources": sources},
            ttl=self._settings.cache_ttl,
        )

        await self._save_messages(session_id, message, response)
        return response, session_id, sources, False

    async def _save_messages(
        self, session_id: str, user_message: str, assistant_message: str
    ) -> None:
        user_msg = ChatMessage(session_id=session_id, role="user", content=user_message)
        await self._cache.save_chat_message(session_id, user_msg)

        assistant_msg = ChatMessage(
            session_id=session_id, role="assistant", content=assistant_message
        )
        await self._cache.save_chat_message(session_id, assistant_msg)

    def _generate_cache_key(self, message: str) -> str:
        hash_val = hashlib.md5(message.lower().strip().encode()).hexdigest()
        return f"rag:response:{hash_val}"
