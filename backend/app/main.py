from contextlib import asynccontextmanager

import logging
import redis.asyncio as aioredis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy import text

from app.config import get_settings
from app.database import engine
from app.routers import admin, auth, bookmarks, documents, feedback, history, providers, search
from app.routers.search import limiter
from app.services.search.embedder import get_embedder
from app.services.search.keyword_search import close_keyword_search
from app.services.search.vector_search import close_vector_search

settings = get_settings()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    get_embedder().load()
    yield
    await close_vector_search()
    await close_keyword_search()
    await app.state.redis.aclose()
    await engine.dispose()


app = FastAPI(
    title="LexSearch API",
    description="AI-powered semantic search for Indian legal judgements",
    version="0.8.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(search.router)
app.include_router(providers.router)
app.include_router(documents.router)
app.include_router(history.router)
app.include_router(bookmarks.router)
app.include_router(feedback.router)
app.include_router(admin.router)


@app.get("/api/health")
async def health_check():
    checks = {"api": "ok", "database": "unknown", "redis": "unknown", "elasticsearch": "unknown"}

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception:
        checks["database"] = "error"
        logger.exception("Database health check failed")

    try:
        await app.state.redis.ping()
        checks["redis"] = "ok"
    except Exception:
        checks["redis"] = "error"
        logger.exception("Redis health check failed")

    try:
        import httpx

        headers: dict[str, str] = {}
        if settings.elasticsearch_api_key_or_none:
            headers["Authorization"] = f"ApiKey {settings.elasticsearch_api_key_or_none}"

        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{settings.elasticsearch_url.rstrip('/')}/_cluster/health",
                headers=headers,
            )
            if response.status_code == 200:
                checks["elasticsearch"] = "ok"
            else:
                checks["elasticsearch"] = "error"
                logger.warning("Elasticsearch health returned %s", response.status_code)
    except Exception:
        checks["elasticsearch"] = "error"
        logger.exception("Elasticsearch health check failed")

    overall = all(v == "ok" for v in checks.values())
    return {
        "status": "healthy" if overall else "degraded",
        "environment": settings.environment,
        "checks": checks,
    }
