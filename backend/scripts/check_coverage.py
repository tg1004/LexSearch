"""Quick diagnostic: document coverage and index counts."""
import asyncio

import httpx
from qdrant_client import QdrantClient
from sqlalchemy import text

from app.database import engine


async def main() -> None:
    async with engine.connect() as conn:
        docs = (await conn.execute(text("SELECT COUNT(*) FROM documents"))).scalar()
        privacy_docs = (
            await conn.execute(
                text(
                    "SELECT COUNT(*) FROM documents "
                    "WHERE title ILIKE '%privacy%' OR full_text ILIKE '%privacy%'"
                )
            )
        ).scalar()
        puttaswamy_docs = (
            await conn.execute(
                text("SELECT COUNT(*) FROM documents WHERE full_text ILIKE '%Puttaswamy%'")
            )
        ).scalar()
        print(f"Postgres documents: {docs}")
        print(f"Postgres chunks: {chunks}")
        print(f"Docs mentioning privacy: {privacy_docs}")
        print(f"Docs mentioning Puttaswamy: {puttaswamy_docs}")

        rows = (
            await conn.execute(
                text(
                    "SELECT title, court FROM documents "
                    "WHERE full_text ILIKE '%privacy%' LIMIT 8"
                )
            )
        ).fetchall()
        print("Sample privacy-related docs:")
        for title, court in rows:
            print(f"  - {(title or '')[:75]} | {court}")

    es = httpx.get("http://localhost:9200/legal_judgements/_count", timeout=10)
    print(f"Elasticsearch chunks: {es.json().get('count')}")

    qdrant = QdrantClient(url="http://localhost:6333")
    info = qdrant.get_collection("legal_judgements")
    print(f"Qdrant points: {info.points_count}")


if __name__ == "__main__":
    asyncio.run(main())
