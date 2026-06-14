"""Store document metadata in PostgreSQL."""

from __future__ import annotations

import logging
from datetime import date

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from data_pipeline.config import PipelineSettings
from data_pipeline.models import ProcessedDocument

logger = logging.getLogger(__name__)


def _import_document_model():
    import sys
    from pathlib import Path

    backend_path = Path(__file__).resolve().parents[2] / "backend"
    if str(backend_path) not in sys.path:
        sys.path.insert(0, str(backend_path))

    from app.models.document_meta import Document

    return Document


def store_documents(documents: list[ProcessedDocument], settings: PipelineSettings | None = None) -> int:
    settings = settings or PipelineSettings.from_env()
    Document = _import_document_model()

    engine = create_engine(settings.database_url, pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=engine)

    stored = 0
    with SessionLocal() as session:
        for doc in documents:
            existing = session.execute(select(Document).where(Document.id == doc.id)).scalar_one_or_none()
            if existing:
                existing.title = doc.title[:500]
                existing.court = doc.court
                existing.date = doc.date
                existing.case_type = doc.case_type
                existing.outcome = doc.outcome
                existing.judges = doc.judges or None
                existing.full_text_length = doc.full_text_length
                existing.url = doc.url
            else:
                session.add(
                    Document(
                        id=doc.id,
                        title=doc.title[:500],
                        court=doc.court,
                        date=doc.date,
                        case_type=doc.case_type,
                        outcome=doc.outcome,
                        judges=doc.judges or None,
                        full_text_length=doc.full_text_length,
                        url=doc.url,
                    )
                )
            stored += 1
        session.commit()

    logger.info("Stored %s documents in PostgreSQL", stored)
    return stored


def store_documents_from_file(processed_path, settings: PipelineSettings | None = None) -> int:
    from data_pipeline.utils import load_jsonl

    records = load_jsonl(processed_path)
    documents = [ProcessedDocument.from_dict(record) for record in records]
    return store_documents(documents, settings=settings)
