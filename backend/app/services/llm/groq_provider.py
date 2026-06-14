from __future__ import annotations

import logging

from groq import AsyncGroq

from app.config import Settings, get_settings
from app.services.llm.base_provider import BaseLLMProvider

logger = logging.getLogger(__name__)


class GroqProvider(BaseLLMProvider):
    name = "groq"

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.model = self.settings.groq_model
        self._client: AsyncGroq | None = None

    def _get_client(self) -> AsyncGroq:
        api_key = self.settings.groq_api_key_or_none
        if not api_key:
            raise ValueError("GROQ_API_KEY is not configured")
        if self._client is None:
            self._client = AsyncGroq(api_key=api_key)
        return self._client

    async def generate(self, prompt: str) -> str:
        client = self._get_client()
        response = await client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=2048,
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Groq returned empty response")
        return content.strip()

    async def is_available(self) -> bool:
        return bool(self.settings.groq_api_key_or_none)
