from fastapi import APIRouter, Depends

from app.config import get_settings
from app.schemas.providers import ProviderInfo, ProvidersResponse
from app.services.llm.llm_service import LLMService, get_llm_service

router = APIRouter(prefix="/api", tags=["providers"])


@router.get("/providers", response_model=ProvidersResponse)
async def list_providers(llm_service: LLMService = Depends(get_llm_service)) -> ProvidersResponse:
    settings = get_settings()
    availability = await llm_service.check_availability()

    providers = [
        ProviderInfo(
            name="auto",
            label="Auto (Recommended)",
            model=None,
            available=availability.get("groq", False) or availability.get("gemini", False),
        ),
        ProviderInfo(
            name="groq",
            label="Groq (Fastest)",
            model=settings.groq_model,
            available=availability.get("groq", False),
        ),
        ProviderInfo(
            name="gemini",
            label="Gemini (Balanced)",
            model=settings.gemini_model,
            available=availability.get("gemini", False),
        ),
    ]

    return ProvidersResponse(providers=providers)
