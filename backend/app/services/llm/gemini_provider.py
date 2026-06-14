from __future__ import annotations

import asyncio
import logging

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

from app.config import Settings, get_settings
from app.services.llm.base_provider import BaseLLMProvider

logger = logging.getLogger(__name__)

# Tried in order if the configured model returns 404.
GEMINI_MODEL_FALLBACKS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-flash-latest",
]


class GeminiProvider(BaseLLMProvider):
    name = "gemini"

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.model = self.settings.gemini_model
        self._configured = False

    def _configure(self) -> None:
        api_key = self.settings.gemini_api_key_or_none
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not configured")
        if not self._configured:
            genai.configure(api_key=api_key)
            self._configured = True

    def _generate_sync(self, prompt: str, model_name: str) -> str:
        self._configure()
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(temperature=0.2, max_output_tokens=2048),
        )
        text = response.text
        if not text:
            raise ValueError("Gemini returned empty response")
        return text.strip()

    async def generate(self, prompt: str) -> str:
        models_to_try = [self.model] + [
            name for name in GEMINI_MODEL_FALLBACKS if name != self.model
        ]
        last_error: Exception | None = None

        for model_name in models_to_try:
            try:
                text = await asyncio.to_thread(self._generate_sync, prompt, model_name)
                self.model = model_name
                return text
            except google_exceptions.NotFound as exc:
                logger.warning("Gemini model %s not found, trying next: %s", model_name, exc)
                last_error = exc
            except google_exceptions.ResourceExhausted as exc:
                logger.warning("Gemini quota/rate limit on %s, trying next: %s", model_name, exc)
                last_error = exc
            except Exception as exc:
                logger.warning("Gemini error on %s: %s", model_name, exc)
                last_error = exc

        if last_error:
            raise last_error
        raise ValueError("No Gemini models available")

    async def is_available(self) -> bool:
        return bool(self.settings.gemini_api_key_or_none)
