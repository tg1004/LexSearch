from __future__ import annotations

import logging

import httpx

from app.config import Settings, get_settings
from app.services.llm.base_provider import BaseLLMProvider

logger = logging.getLogger(__name__)


class OllamaProvider(BaseLLMProvider):
    """Optional local fallback — not used in default groq,gemini chain."""

    name = "ollama"

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.model = self.settings.ollama_model
        self.base_url = self.settings.ollama_base_url.rstrip("/")

    async def generate(self, prompt: str) -> str:
        async with httpx.AsyncClient(timeout=self.settings.llm_timeout_seconds) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
            )
            response.raise_for_status()
            data = response.json()
            text = data.get("response", "").strip()
            if not text:
                raise ValueError("Ollama returned empty response")
            return text

    async def is_available(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception:
            return False
