"""Generate embeddings with sentence-transformers and store chunks in Qdrant."""

from __future__ import annotations

import logging
import uuid
from pathlib import Path
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

from data_pipeline.config import PipelineSettings
from data_pipeline.models import DocumentChunk, ProcessedDocument

logger = logging.getLogger(__name__)


def get_qdrant_client(settings: PipelineSettings | None = None) -> QdrantClient:
    settings = settings or PipelineSettings.from_env()
    api_key = (settings.qdrant_api_key or "").strip()
    if api_key:
        return QdrantClient(url=settings.qdrant_url, api_key=api_key)
    return QdrantClient(url=settings.qdrant_url)


def ensure_collection(client: QdrantClient, settings: PipelineSettings, recreate: bool = False) -> None:
    collections = {collection.name for collection in client.get_collections().collections}
    if settings.qdrant_collection_name in collections:
        if recreate:
            client.delete_collection(settings.qdrant_collection_name)
            logger.info("Deleted Qdrant collection %s", settings.qdrant_collection_name)
        else:
            logger.info("Qdrant collection %s already exists", settings.qdrant_collection_name)
            return

    client.create_collection(
        collection_name=settings.qdrant_collection_name,
        vectors_config=qmodels.VectorParams(
            size=settings.embedding_dimension,
            distance=qmodels.Distance.COSINE,
        ),
    )
    logger.info("Created Qdrant collection %s (dim=%s)", settings.qdrant_collection_name, settings.embedding_dimension)


def chunk_point_id(chunk: DocumentChunk) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{chunk.document_id}:{chunk.chunk_index}"))


def chunk_to_payload(
    chunk: DocumentChunk,
    document: "ProcessedDocument | None" = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "document_id": chunk.document_id,
        "chunk_index": chunk.chunk_index,
        "text": chunk.text,
        "title": chunk.title,
        "court": chunk.court,
        "case_type": chunk.case_type,
        "char_start": chunk.char_start,
        "char_end": chunk.char_end,
    }
    if chunk.date:
        payload["date"] = chunk.date.isoformat()
    if document and document.outcome:
        payload["outcome"] = document.outcome
    return payload


def embed_texts(model: SentenceTransformer, texts: list[str], batch_size: int = 64) -> list[list[float]]:
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=len(texts) > batch_size,
        normalize_embeddings=True,
    )
    return embeddings.tolist()


def store_chunks_in_qdrant(
    chunks: list[DocumentChunk],
    settings: PipelineSettings | None = None,
    recreate_collection: bool = False,
    batch_size: int = 64,
    documents_by_id: dict[str, ProcessedDocument] | None = None,
) -> int:
    settings = settings or PipelineSettings.from_env()
    client = get_qdrant_client(settings)
    ensure_collection(client, settings, recreate=recreate_collection)

    documents_by_id = documents_by_id or {}

    logger.info("Loading embedding model %s ...", settings.embedding_model)
    model = SentenceTransformer(settings.embedding_model)

    stored = 0
    for start in tqdm(range(0, len(chunks), batch_size), desc="Embedding + Qdrant upload"):
        batch = chunks[start : start + batch_size]
        vectors = embed_texts(model, [chunk.text for chunk in batch], batch_size=batch_size)
        points = [
            qmodels.PointStruct(
                id=chunk_point_id(chunk),
                vector=vector,
                payload=chunk_to_payload(chunk, documents_by_id.get(chunk.document_id)),
            )
            for chunk, vector in zip(batch, vectors)
        ]
        client.upsert(collection_name=settings.qdrant_collection_name, points=points)
        stored += len(points)

    collection_info = client.get_collection(settings.qdrant_collection_name)
    logger.info(
        "Qdrant collection %s now has %s points",
        settings.qdrant_collection_name,
        collection_info.points_count,
    )
    return stored


def store_from_file(
    chunks_path: Path,
    settings: PipelineSettings | None = None,
    recreate_collection: bool = False,
    processed_path: Path | None = None,
) -> int:
    from data_pipeline.config import PROCESSED_DIR
    from data_pipeline.utils import load_jsonl

    records = load_jsonl(chunks_path)
    chunks = [DocumentChunk.from_dict(record) for record in records]

    documents_by_id: dict[str, ProcessedDocument] = {}
    resolved_processed = processed_path or (PROCESSED_DIR / "documents.jsonl")
    if resolved_processed.exists():
        for record in load_jsonl(resolved_processed):
            doc = ProcessedDocument.from_dict(record)
            documents_by_id[doc.id] = doc

    return store_chunks_in_qdrant(
        chunks,
        settings=settings,
        recreate_collection=recreate_collection,
        documents_by_id=documents_by_id,
    )


def get_collection_stats(settings: PipelineSettings | None = None) -> dict[str, Any]:
    settings = settings or PipelineSettings.from_env()
    client = get_qdrant_client(settings)
    try:
        info = client.get_collection(settings.qdrant_collection_name)
        return {"points_count": info.points_count, "status": str(info.status)}
    except Exception as exc:
        return {"error": str(exc)}
