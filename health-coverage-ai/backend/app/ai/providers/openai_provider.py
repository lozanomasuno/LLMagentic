"""OpenAI provider — production implementation (Sprint 3)."""

from typing import Any

from openai import AsyncOpenAI

from app.ai.providers.base_provider import LLMProvider


class OpenAIProvider(LLMProvider):
    """
    Async OpenAI GPT provider.

    Wraps AsyncOpenAI so the rest of the application never imports openai
    directly — only through this adapter, keeping the LLMProvider contract.
    """

    def __init__(self, api_key: str, model: str = "gpt-4o") -> None:
        self._api_key = api_key
        self._model = model
        self._client = AsyncOpenAI(api_key=api_key)

    @property
    def model_name(self) -> str:
        return self._model

    async def complete(self, prompt: str, **kwargs: Any) -> str:
        """Single-turn completion (user message only)."""
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
            temperature=kwargs.get("temperature", 0.1),
            max_tokens=kwargs.get("max_tokens", 2000),
        )
        return response.choices[0].message.content or ""

    async def complete_with_system(
        self, system: str, user: str, **kwargs: Any
    ) -> str:
        """Two-turn completion with an explicit system prompt."""
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=kwargs.get("temperature", 0.1),
            max_tokens=kwargs.get("max_tokens", 2000),
        )
        return response.choices[0].message.content or ""

    async def embed(self, text: str) -> list[float]:
        """Generate text embeddings using text-embedding-3-small."""
        response = await self._client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
        )
        return response.data[0].embedding
