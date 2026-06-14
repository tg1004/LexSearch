"""Index document chunks in Elasticsearch with explicit mappings."""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any, Iterator

from elasticsearch import Elasticsearch, helpers
from elasticsearch.exceptions import ApiError, NotFoundError

from data_pipeline.config import PipelineSettings
from data_pipeline.models import DocumentChunk, ProcessedDocument

logger = logging.getLogger(__name__)

# Keep batches small — chunk_text only (no duplicated full judgement per chunk).
DEFAULT_BATCH_SIZE = 100

INDEX_MAPPING: dict[str, Any] = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
        "analysis": {
            "analyzer": {
                "legal_text_analyzer": {
                    "type": "standard",
                    "stopwords": "_english_",
                }
            }
        },
    },
    "mappings": {
        "properties": {
            "document_id": {"type": "keyword"},
            "chunk_id": {"type": "keyword"},
            "chunk_index": {"type": "integer"},
            "title": {
                "type": "text",
                "analyzer": "legal_text_analyzer",
                "fields": {"keyword": {"type": "keyword"}},
            },
            "court": {"type": "keyword"},
            "date": {"type": "date", "format": "yyyy-MM-dd||strict_date_optional_time||epoch_millis"},
            "case_type": {"type": "keyword"},
            "outcome": {"type": "keyword"},
            "judges": {"type": "keyword"},
            "url": {"type": "keyword"},
            "chunk_text": {"type": "text", "analyzer": "legal_text_analyzer"},
            "char_start": {"type": "integer"},
            "char_end": {"type": "integer"},
        }
    },
}


def get_client(settings: PipelineSettings | None = None) -> Elasticsearch:
    settings = settings or PipelineSettings.from_env()
    client_kwargs: dict[str, Any] = {"request_timeout": 120}
    if settings.elasticsearch_api_key:
        client_kwargs["api_key"] = settings.elasticsearch_api_key
    elif settings.elasticsearch_user and settings.elasticsearch_password:
        client_kwargs["basic_auth"] = (settings.elasticsearch_user, settings.elasticsearch_password)
    return Elasticsearch(settings.elasticsearch_url, **client_kwargs)


def ensure_index(client: Elasticsearch, index_name: str, recreate: bool = False) -> None:
    if client.indices.exists(index=index_name):
        if recreate:
            client.indices.delete(index=index_name)
            logger.info("Deleted existing index %s", index_name)
        else:
            logger.info("Index %s already exists", index_name)
            return

    client.indices.create(
        index=index_name,
        settings=INDEX_MAPPING["settings"],
        mappings=INDEX_MAPPING["mappings"],
    )
    logger.info("Created Elasticsearch index %s", index_name)


def _chunk_doc_id(chunk: DocumentChunk) -> str:
    return f"{chunk.document_id}_{chunk.chunk_index}"


def _chunk_to_action(
    chunk: DocumentChunk,
    index_name: str,
    document: ProcessedDocument | None = None,
) -> dict[str, Any]:
    source: dict[str, Any] = {
        "document_id": chunk.document_id,
        "chunk_id": _chunk_doc_id(chunk),
        "chunk_index": chunk.chunk_index,
        "title": chunk.title,
        "court": chunk.court,
        "case_type": chunk.case_type,
        "chunk_text": chunk.text,
        "char_start": chunk.char_start,
        "char_end": chunk.char_end,
    }
    if chunk.date:
        source["date"] = chunk.date.isoformat()
    if document:
        if document.outcome:
            source["outcome"] = document.outcome
        if document.judges:
            source["judges"] = document.judges
        if document.url:
            source["url"] = document.url

    return {
        "_index": index_name,
        "_id": _chunk_doc_id(chunk),
        "_source": source,
    }


def _bulk_batch(
    client: Elasticsearch,
    actions: list[dict[str, Any]],
    *,
    max_retries: int = 5,
) -> tuple[int, list[Any]]:
    for attempt in range(max_retries + 1):
        try:
            success, errors = helpers.bulk(
                client,
                actions,
                raise_on_error=False,
                request_timeout=120,
            )
            if errors:
                logger.warning("Elasticsearch bulk batch had %s errors", len(errors))
            return success, errors or []
        except ApiError as exc:
            if exc.status_code == 429 and attempt < max_retries:
                wait_seconds = min(2 ** attempt, 30)
                logger.warning(
                    "Elasticsearch rate-limited bulk request (attempt %s/%s), retrying in %ss",
                    attempt + 1,
                    max_retries,
                    wait_seconds,
                )
                time.sleep(wait_seconds)
                continue
            raise
    return 0, []


def _iter_batches(items: list[DocumentChunk], batch_size: int) -> Iterator[list[DocumentChunk]]:
    for start in range(0, len(items), batch_size):
        yield items[start : start + batch_size]


def index_chunks(
    chunks: list[DocumentChunk],
    documents_by_id: dict[str, ProcessedDocument] | None = None,
    settings: PipelineSettings | None = None,
    recreate_index: bool = False,
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> int:
    settings = settings or PipelineSettings.from_env()
    client = get_client(settings)
    ensure_index(client, settings.elasticsearch_index, recreate=recreate_index)

    documents_by_id = documents_by_id or {}
    total_indexed = 0
    total_batches = (len(chunks) + batch_size - 1) // batch_size

    for batch_number, batch in enumerate(_iter_batches(chunks, batch_size), start=1):
        actions = [
            _chunk_to_action(
                chunk,
                settings.elasticsearch_index,
                document=documents_by_id.get(chunk.document_id),
            )
            for chunk in batch
        ]
        success, _ = _bulk_batch(client, actions)
        total_indexed += success

        if batch_number % 50 == 0 or batch_number == total_batches:
            logger.info(
                "Elasticsearch progress: %s/%s batches, %s chunks indexed",
                batch_number,
                total_batches,
                total_indexed,
            )

    client.indices.refresh(index=settings.elasticsearch_index)
    logger.info("Indexed %s chunks in Elasticsearch index %s", total_indexed, settings.elasticsearch_index)
    return total_indexed


def index_from_files(
    chunks_path: Path,
    processed_path: Path | None = None,
    settings: PipelineSettings | None = None,
    recreate_index: bool = False,
) -> int:
    from data_pipeline.utils import load_jsonl

    chunk_records = load_jsonl(chunks_path)
    chunks = [DocumentChunk.from_dict(record) for record in chunk_records]

    documents_by_id: dict[str, ProcessedDocument] = {}
    if processed_path and processed_path.exists():
        for record in load_jsonl(processed_path):
            doc = ProcessedDocument.from_dict(record)
            documents_by_id[doc.id] = doc

    return index_chunks(chunks, documents_by_id=documents_by_id, settings=settings, recreate_index=recreate_index)


def get_index_stats(settings: PipelineSettings | None = None) -> dict[str, Any]:
    settings = settings or PipelineSettings.from_env()
    client = get_client(settings)
    try:
        return client.count(index=settings.elasticsearch_index)
    except NotFoundError:
        return {"count": 0}
