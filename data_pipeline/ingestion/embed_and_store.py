"""Generate embeddings with sentence-transformers and store chunks in Qdrant."""

from __future__ import annotations

import json
import logging
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from qdrant_client.http.exceptions import ResponseHandlingException
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

from data_pipeline.config import CHUNKS_DIR, PipelineSettings
from data_pipeline.models import DocumentChunk, ProcessedDocument

logger = logging.getLogger(__name__)

CHECKPOINT_PATH = CHUNKS_DIR.parent / ".qdrant_upload_checkpoint.json"
MAX_UPSERT_RETRIES = 5


def get_qdrant_client(settings: PipelineSettings | None = None) -> QdrantClient:
    settings = settings or PipelineSettings.from_env()
    api_key = (settings.qdrant_api_key or "").strip()
    client_kwargs: dict[str, Any] = {
        "url": settings.qdrant_url_normalized,
        "timeout": settings.qdrant_timeout_seconds,
    }
    if api_key:
        client_kwargs["api_key"] = api_key
    return QdrantClient(**client_kwargs)


def _load_checkpoint(settings: PipelineSettings, batch_size: int, total_chunks: int) -> int:
    if not CHECKPOINT_PATH.exists():
        return 0

    try:
        data = json.loads(CHECKPOINT_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        logger.warning("Ignoring corrupt Qdrant checkpoint file")
        return 0

    if (
        data.get("collection") != settings.qdrant_collection_name
        or data.get("qdrant_url") != settings.qdrant_url_normalized
        or data.get("batch_size") != batch_size
        or data.get("total_chunks") != total_chunks
    ):
        logger.warning("Qdrant checkpoint does not match current run — starting from beginning")
        return 0

    start_index = int(data.get("next_chunk_index", 0))
    if start_index > 0:
        logger.info(
            "Resuming Qdrant upload from chunk %s/%s (%.1f%%)",
            start_index,
            total_chunks,
            (start_index / total_chunks) * 100,
        )
    return start_index


def _save_checkpoint(
    settings: PipelineSettings,
    batch_size: int,
    total_chunks: int,
    next_chunk_index: int,
) -> None:
    CHECKPOINT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "collection": settings.qdrant_collection_name,
        "qdrant_url": settings.qdrant_url_normalized,
        "batch_size": batch_size,
        "total_chunks": total_chunks,
        "next_chunk_index": next_chunk_index,
        "updated_at": datetime.now(UTC).isoformat(),
    }
    CHECKPOINT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _clear_checkpoint() -> None:
    if CHECKPOINT_PATH.exists():
        CHECKPOINT_PATH.unlink()


def upsert_with_retry(
    client: QdrantClient,
    collection_name: str,
    points: list[qmodels.PointStruct],
    settings: PipelineSettings,
) -> None:
    last_error: Exception | None = None
    for attempt in range(1, MAX_UPSERT_RETRIES + 1):
        try:
            client.upsert(
                collection_name=collection_name,
                points=points,
                wait=True,
            )
            return
        except (ResponseHandlingException, TimeoutError, OSError) as exc:
            last_error = exc
            if attempt >= MAX_UPSERT_RETRIES:
                break
            delay = min(2 ** (attempt - 1) * 5, 60)
            logger.warning(
                "Qdrant upsert failed (attempt %s/%s, %s points): %s — retrying in %ss",
                attempt,
                MAX_UPSERT_RETRIES,
                len(points),
                exc,
                delay,
            )
            time.sleep(delay)

    raise RuntimeError(f"Qdrant upsert failed after {MAX_UPSERT_RETRIES} attempts") from last_error


def ensure_collection(client: QdrantClient, settings: PipelineSettings, recreate: bool = False) -> None:
    collections = {collection.name for collection in client.get_collections().collections}
    if settings.qdrant_collection_name in collections:
        if recreate:
            client.delete_collection(settings.qdrant_collection_name)
            _clear_checkpoint()
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
    batch_size: int | None = None,
    documents_by_id: dict[str, ProcessedDocument] | None = None,
) -> int:
    settings = settings or PipelineSettings.from_env()
    batch_size = batch_size or settings.qdrant_upload_batch_size
    client = get_qdrant_client(settings)
    ensure_collection(client, settings, recreate=recreate_collection)

    documents_by_id = documents_by_id or {}
    start_index = 0 if recreate_collection else _load_checkpoint(settings, batch_size, len(chunks))

    if settings.is_qdrant_cloud:
        logger.info(
            "Qdrant Cloud upload: batch_size=%s, timeout=%ss",
            batch_size,
            settings.qdrant_timeout_seconds,
        )

    logger.info("Loading embedding model %s ...", settings.embedding_model)
    model = SentenceTransformer(settings.embedding_model)

    stored = 0
    batch_indices = range(start_index, len(chunks), batch_size)
    for start in tqdm(batch_indices, desc="Embedding + Qdrant upload"):
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
        upsert_with_retry(client, settings.qdrant_collection_name, points, settings)
        stored += len(points)
        _save_checkpoint(settings, batch_size, len(chunks), start + len(batch))

    _clear_checkpoint()

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
