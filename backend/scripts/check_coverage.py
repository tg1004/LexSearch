"""Quick diagnostic: document coverage and index counts."""

import asyncio
import os

import httpx
from qdrant_client import QdrantClient
from sqlalchemy import text

from app.config import get_settings
from app.database import engine


async def main() -> None:
    settings = get_settings()
    chunks_path = settings.chunks_data_path
    chunk_count = 0
    if os.path.isfile(chunks_path):
        with open(chunks_path, encoding="utf-8") as handle:
            chunk_count = sum(1 for line in handle if line.strip())

    async with engine.connect() as conn:
        docs = (await conn.execute(text("SELECT COUNT(*) FROM documents"))).scalar()
        privacy_docs = (
            await conn.execute(
                text(
                    "SELECT COUNT(*) FROM documents "
                    "WHERE title ILIKE '%privacy%'"
                )
            )
        ).scalar()
        print(f"Postgres documents: {docs}")
        print(f"Local chunks file: {chunk_count}")
        print(f"Docs with 'privacy' in title: {privacy_docs}")

    es_headers = {}
    if settings.elasticsearch_api_key_or_none:
        es_headers["Authorization"] = f"ApiKey {settings.elasticsearch_api_key_or_none}"

    es = httpx.get(
        f"{settings.elasticsearch_url.rstrip('/')}/{settings.elasticsearch_index}/_count",
        headers=es_headers,
        timeout=30,
    )
    print(f"Elasticsearch chunks: {es.json().get('count')}")

    qdrant_kwargs: dict = {"url": settings.qdrant_url.rstrip("/")}
    if settings.qdrant_api_key_or_none:
        qdrant_kwargs["api_key"] = settings.qdrant_api_key_or_none
    qdrant = QdrantClient(**qdrant_kwargs)
    info = qdrant.get_collection(settings.qdrant_collection_name)
    print(f"Qdrant points: {info.points_count}")


if __name__ == "__main__":
    asyncio.run(main())
