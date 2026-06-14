from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LLMResponse:
    text: str
    provider: str
    model: str


class BaseLLMProvider(ABC):
    name: str
    model: str

    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """Generate text from a prompt."""

    @abstractmethod
    async def is_available(self) -> bool:
        """Check whether this provider is configured and reachable."""
