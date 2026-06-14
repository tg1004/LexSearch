"""Process raw scraped documents into cleaned docs and chunks."""

from __future__ import annotations

import logging
from pathlib import Path

from tqdm import tqdm

from data_pipeline.config import CHUNKS_DIR, PROCESSED_DIR, RAW_DIR, ensure_data_dirs
from data_pipeline.models import ProcessedDocument, RawDocument
from data_pipeline.processor.chunker import chunk_documents
from data_pipeline.processor.metadata_extractor import extract_metadata
from data_pipeline.processor.text_cleaner import clean_text
from data_pipeline.utils import load_jsonl, save_jsonl

logger = logging.getLogger(__name__)


def process_raw_documents(raw_path: Path | None = None) -> tuple[Path, Path]:
    ensure_data_dirs()
    raw_path = raw_path or (RAW_DIR / "documents.jsonl")
    processed_path = PROCESSED_DIR / "documents.jsonl"
    chunks_path = CHUNKS_DIR / "chunks.jsonl"

    raw_records = load_jsonl(raw_path)
    if not raw_records:
        raise FileNotFoundError(f"No raw documents found at {raw_path}. Run scrape step first.")

    processed_docs: list[ProcessedDocument] = []
    for record in tqdm(raw_records, desc="Processing documents"):
        raw = RawDocument.from_dict(record)
        cleaned = clean_text(raw.full_text)
        metadata = extract_metadata(raw, cleaned)

        processed_docs.append(
            ProcessedDocument(
                id=raw.id,
                title=raw.title,
                full_text=cleaned,
                url=raw.url,
                court=metadata.court,
                date=metadata.date,
                case_type=metadata.case_type,
                outcome=metadata.outcome,
                judges=metadata.judges,
                full_text_length=len(cleaned),
            )
        )

    save_jsonl(processed_path, [doc.to_dict() for doc in processed_docs])
    logger.info("Saved %s processed documents to %s", len(processed_docs), processed_path)

    chunks = chunk_documents(processed_docs)
    save_jsonl(chunks_path, [chunk.to_dict() for chunk in chunks])
    logger.info("Saved %s chunks to %s", len(chunks), chunks_path)

    return processed_path, chunks_path
