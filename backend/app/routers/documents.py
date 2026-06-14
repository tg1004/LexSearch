from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.routers.search import limiter
from app.schemas.document import DocumentResponse, DocumentSummaryResponse, HighlightResponse
from app.services.cache.redis_cache import RedisCache
from app.services.document.document_service import DocumentService, get_document_service
from app.services.document.summary_service import SummaryService

router = APIRouter(prefix="/api", tags=["documents"])


def get_redis_cache(request: Request) -> RedisCache:
    return RedisCache(request.app.state.redis)


def get_summary_service(
    request: Request,
    redis_cache: RedisCache = Depends(get_redis_cache),
) -> SummaryService:
    return SummaryService(redis_cache=redis_cache)


@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    document_service: DocumentService = Depends(get_document_service),
    summary_service: SummaryService = Depends(get_summary_service),
) -> DocumentResponse:
    cached_summary = await summary_service.get_cached_summary(document_id)
    return await document_service.get_document(db, document_id, cached_summary=cached_summary)


@router.post("/documents/{document_id}/summary", response_model=DocumentSummaryResponse)
@limiter.limit("10/minute")
async def generate_document_summary(
    request: Request,
    document_id: str,
    db: AsyncSession = Depends(get_db),
    document_service: DocumentService = Depends(get_document_service),
    summary_service: SummaryService = Depends(get_summary_service),
) -> DocumentSummaryResponse:
    document = await document_service.get_document(db, document_id)
    summary, provider_used = await summary_service.generate_summary(document_id, document.full_text)
    return DocumentSummaryResponse(
        document_id=document_id,
        summary=summary,
        provider_used=provider_used,
    )


@router.get("/documents/{document_id}/highlight", response_model=HighlightResponse)
async def get_document_highlight(
    document_id: str,
    chunk_index: int,
    document_service: DocumentService = Depends(get_document_service),
) -> HighlightResponse:
    return document_service.get_highlight(document_id, chunk_index)
