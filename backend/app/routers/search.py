from fastapi import APIRouter, BackgroundTasks, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database import AsyncSessionLocal
from app.models.user import User
from app.schemas.search import SearchRequest, SearchResponse
from app.services.cache.redis_cache import RedisCache
from app.services.rag.rag_service import RAGService
from app.services.user import history_service
from app.utils.auth_utils import get_optional_user

router = APIRouter(prefix="/api", tags=["search"])
limiter = Limiter(key_func=get_remote_address)


def get_rag_service(request: Request) -> RAGService:
    redis_cache = RedisCache(request.app.state.redis)
    return RAGService(redis_cache=redis_cache)


async def _save_history(
    user_id,
    query: str,
    provider_used: str | None,
    result_count: int,
) -> None:
    async with AsyncSessionLocal() as session:
        try:
            await history_service.save_search_history(
                session,
                user_id=user_id,
                query=query,
                provider_used=provider_used,
                result_count=result_count,
            )
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@router.post("/search", response_model=SearchResponse)
@limiter.limit("20/minute")
async def search(
    request: Request,
    body: SearchRequest,
    background_tasks: BackgroundTasks,
    rag_service: RAGService = Depends(get_rag_service),
    current_user: User | None = Depends(get_optional_user),
) -> SearchResponse:
    """
    Full RAG search: hybrid retrieval + AI answer with citations.
    Fallback chain: Groq → Gemini (configurable via LLM_FALLBACK_ORDER).
    """
    response = await rag_service.search(
        query=body.query,
        filters=body.filters,
        page=body.page,
        preferred_provider=body.preferred_provider,
    )

    if current_user:
        background_tasks.add_task(
            _save_history,
            current_user.id,
            body.query,
            response.provider_used,
            response.result_count,
        )

    return response
