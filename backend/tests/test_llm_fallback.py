from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.llm.llm_service import AllProvidersFailedError, LLMService


@pytest.mark.asyncio
async def test_fallback_from_groq_to_gemini():
    groq = MagicMock()
    groq.is_available = AsyncMock(return_value=True)
    groq.generate = AsyncMock(side_effect=Exception("rate limited"))
    groq.model = "llama-test"

    gemini = MagicMock()
    gemini.is_available = AsyncMock(return_value=True)
    gemini.generate = AsyncMock(return_value="Answer with [1] citation.")
    gemini.model = "gemini-test"

    service = LLMService()
    service.providers = {"groq": groq, "gemini": gemini}

    response = await service.generate("test prompt", preferred_provider="auto")

    assert response.provider == "gemini"
    assert "Answer" in response.text
    groq.generate.assert_awaited_once()
    gemini.generate.assert_awaited_once()


@pytest.mark.asyncio
async def test_all_providers_fail():
    groq = MagicMock()
    groq.is_available = AsyncMock(return_value=True)
    groq.generate = AsyncMock(side_effect=Exception("fail"))
    groq.model = "llama-test"

    gemini = MagicMock()
    gemini.is_available = AsyncMock(return_value=True)
    gemini.generate = AsyncMock(side_effect=Exception("fail"))
    gemini.model = "gemini-test"

    service = LLMService()
    service.providers = {"groq": groq, "gemini": gemini}

    with pytest.raises(AllProvidersFailedError):
        await service.generate("test prompt")
