"""Abstract LLM provider interface.

All LLM integrations must implement this contract.
The rest of the application depends on this abstraction,
never on a specific provider (OpenAI, Anthropic, Azure, Ollama, etc.).
"""

from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    """Contract for all LLM provider implementations."""

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the underlying model identifier."""

    @abstractmethod
    async def complete(self, prompt: str, **kwargs: Any) -> str:
        """
        Generate a text completion for the given prompt.

        Args:
            prompt: The input prompt.
            **kwargs: Provider-specific parameters (temperature, max_tokens, etc.)

        Returns:
            The model's response as a string.
        """

    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        """
        Generate an embedding vector for the given text.

        Args:
            text: The input text to embed.

        Returns:
            A list of floats representing the embedding.
        """

    async def batch_complete(self, prompts: list[str], **kwargs: Any) -> list[str]:
        """
        Default implementation: sequential completion.
        Override for provider-native batching.
        """
        results = []
        for prompt in prompts:
            results.append(await self.complete(prompt, **kwargs))
        return results
