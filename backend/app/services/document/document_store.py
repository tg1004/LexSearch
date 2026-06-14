from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class StoredChunk:
    document_id: str
    chunk_index: int
    text: str
    char_start: int
    char_end: int


class DocumentStore:
    """Loads full judgement text and chunk offsets from pipeline JSONL files."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._full_text_cache: dict[str, str] | None = None
        self._chunk_cache: dict[tuple[str, int], StoredChunk] | None = None

    def _load_full_text_cache(self) -> dict[str, str]:
        if self._full_text_cache is not None:
            return self._full_text_cache

        cache: dict[str, str] = {}
        path = Path(self.settings.processed_documents_path)
        if path.exists():
            with path.open(encoding="utf-8") as handle:
                for line in handle:
                    line = line.strip()
                    if not line:
                        continue
                    record = json.loads(line)
                    doc_id = str(record.get("id", ""))
                    if doc_id:
                        cache[doc_id] = str(record.get("full_text", ""))
        else:
            logger.warning("Processed documents file not found: %s", path)

        self._full_text_cache = cache
        return cache

    def _load_chunk_cache(self) -> dict[tuple[str, int], StoredChunk]:
        if self._chunk_cache is not None:
            return self._chunk_cache

        cache: dict[tuple[str, int], StoredChunk] = {}
        path = Path(self.settings.chunks_data_path)
        if path.exists():
            with path.open(encoding="utf-8") as handle:
                for line in handle:
                    line = line.strip()
                    if not line:
                        continue
                    record = json.loads(line)
                    doc_id = str(record.get("document_id", ""))
                    chunk_index = int(record.get("chunk_index", 0))
                    if not doc_id:
                        continue
                    cache[(doc_id, chunk_index)] = StoredChunk(
                        document_id=doc_id,
                        chunk_index=chunk_index,
                        text=str(record.get("text", "")),
                        char_start=int(record.get("char_start", 0)),
                        char_end=int(record.get("char_end", 0)),
                    )
        else:
            logger.warning("Chunks data file not found: %s", path)

        self._chunk_cache = cache
        return cache

    def get_full_text(self, document_id: str) -> str | None:
        text = self._load_full_text_cache().get(document_id)
        return text if text else None

    def get_chunk(self, document_id: str, chunk_index: int) -> StoredChunk | None:
        return self._load_chunk_cache().get((document_id, chunk_index))


def get_document_store() -> DocumentStore:
    return DocumentStore()
