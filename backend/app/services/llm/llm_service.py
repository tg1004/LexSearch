from __future__ import annotations

import asyncio
import logging

from app.config import Settings, get_settings
from app.services.llm.base_provider import BaseLLMProvider, LLMResponse
from app.services.llm.gemini_provider import GeminiProvider
from app.services.llm.groq_provider import GroqProvider
from app.services.llm.ollama_provider import OllamaProvider

logger = logging.getLogger(__name__)


class AllProvidersFailedError(Exception):
    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__("All LLM providers failed: " + "; ".join(errors))


class LLMService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        all_providers: dict[str, BaseLLMProvider] = {
            "groq": GroqProvider(self.settings),
            "gemini": GeminiProvider(self.settings),
            "ollama": OllamaProvider(self.settings),
        }
        # Only use providers listed in LLM_FALLBACK_ORDER (default: groq,gemini).
        self.providers = {
            name: all_providers[name]
            for name in self.settings.llm_provider_order
            if name in all_providers
        }

    def _resolve_order(self, preferred_provider: str | None) -> list[str]:
        configured_order = [
            name for name in self.settings.llm_provider_order if name in self.providers
        ]
        if not preferred_provider or preferred_provider.lower() == "auto":
            return configured_order

        preferred = preferred_provider.lower()
        if preferred not in self.providers:
            return configured_order

        order = [preferred] + [name for name in configured_order if name != preferred]
        return order

    async def generate(self, prompt: str, preferred_provider: str | None = None) -> LLMResponse:
        order = self._resolve_order(preferred_provider)
        errors: list[str] = []

        for provider_name in order:
            provider = self.providers[provider_name]
            try:
                if not await provider.is_available():
                    errors.append(f"{provider_name}: not configured or unavailable")
                    continue

                text = await asyncio.wait_for(
                    provider.generate(prompt),
                    timeout=self.settings.llm_timeout_seconds,
                )
                logger.info("LLM response from %s (%s)", provider_name, provider.model)
                return LLMResponse(text=text, provider=provider_name, model=provider.model)

            except asyncio.TimeoutError:
                msg = f"{provider_name}: timeout after {self.settings.llm_timeout_seconds}s"
                logger.error(msg)
                errors.append(msg)
            except Exception as exc:
                msg = f"{provider_name}: {exc}"
                logger.error("LLM provider failed: %s", msg)
                errors.append(msg)

        raise AllProvidersFailedError(errors)

    async def check_availability(self) -> dict[str, bool]:
        return {name: await provider.is_available() for name, provider in self.providers.items()}


def get_llm_service() -> LLMService:
    return LLMService()
