"""LLM Service Interface."""

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator


class ILLMService(ABC):
    """Interface untuk LLM Service."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        context: str | None = None,
        chat_history: list[dict] | None = None,
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> str:
        pass

    @abstractmethod
    async def generate_stream(
        self,
        prompt: str,
        context: str | None = None,
        chat_history: list[dict] | None = None,
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> AsyncGenerator[str, None]:
        pass
