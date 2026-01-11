"""Cohere LLM Service Implementation."""

from collections.abc import AsyncGenerator

import cohere

from app.config import get_settings
from app.domain.interfaces.llm_service import ILLMService


class CohereLLMService(ILLMService):
    SYSTEM_PROMPT = """Kamu adalah asisten AI yang membantu menjawab pertanyaan berdasarkan konteks dokumen yang diberikan.

ATURAN PENTING:
1. Jawab HANYA berdasarkan informasi dari konteks yang diberikan
2. Jika informasi tidak ada dalam konteks, katakan "Maaf, saya tidak menemukan informasi tersebut dalam dokumen."
3. Jangan mengarang atau menambahkan informasi yang tidak ada dalam konteks
4. Gunakan bahasa yang sama dengan pertanyaan user
5. Berikan jawaban yang ringkas dan langsung ke inti"""

    def __init__(self, client: cohere.ClientV2 | None = None) -> None:
        self._settings = get_settings()
        self._client = client or cohere.ClientV2(api_key=self._settings.cohere_api_key)
        self._model = self._settings.llm_model

    def _build_messages(
        self,
        prompt: str,
        context: str | None = None,
        chat_history: list[dict] | None = None,
    ) -> list[dict]:
        messages = []
        system_content = self.SYSTEM_PROMPT
        if context:
            system_content += f"\n\nKONTEKS DOKUMEN:\n{context}"
        messages.append({"role": "system", "content": system_content})

        if chat_history:
            for msg in chat_history:
                messages.append({"role": msg["role"], "content": msg["content"]})

        messages.append({"role": "user", "content": prompt})
        return messages

    async def generate(
        self,
        prompt: str,
        context: str | None = None,
        chat_history: list[dict] | None = None,
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> str:
        messages = self._build_messages(prompt, context, chat_history)
        response = self._client.chat(
            model=self._model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.message.content[0].text

    async def generate_stream(
        self,
        prompt: str,
        context: str | None = None,
        chat_history: list[dict] | None = None,
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> AsyncGenerator[str, None]:
        messages = self._build_messages(prompt, context, chat_history)
        stream = self._client.chat_stream(
            model=self._model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        for event in stream:
            if event.type == "content-delta":
                yield event.delta.message.content.text
