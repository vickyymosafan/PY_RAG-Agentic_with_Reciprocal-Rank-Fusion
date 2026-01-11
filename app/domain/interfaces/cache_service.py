"""Cache Service Interface."""

from abc import ABC, abstractmethod
from typing import Any

from app.domain.entities.chat_message import ChatMessage


class ICacheService(ABC):
    """Interface untuk Cache Service."""

    @abstractmethod
    async def get(self, key: str) -> Any | None:
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        pass

    @abstractmethod
    async def get_chat_history(self, session_id: str, limit: int = 20) -> list[ChatMessage]:
        pass

    @abstractmethod
    async def save_chat_message(self, session_id: str, message: ChatMessage) -> bool:
        pass

    @abstractmethod
    async def clear_chat_history(self, session_id: str) -> bool:
        pass
