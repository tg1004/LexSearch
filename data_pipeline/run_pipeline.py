"""
Master data pipeline: scrape → process → ingest.

Usage:
    python -m data_pipeline.run_pipeline --step all --limit 1000
    python -m data_pipeline.run_pipeline --step scrape --limit 50
    python -m data_pipeline.run_pipeline --step process
    python -m data_pipeline.run_pipeline --step ingest
    python -m data_pipeline.run_pipeline --step verify
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from data_pipeline.config import CHUNKS_DIR, PROCESSED_DIR, RAW_DIR, PipelineSettings, ensure_data_dirs
from data_pipeline.ingestion.elasticsearch_index import get_index_stats, index_from_files
from data_pipeline.ingestion.embed_and_store import get_collection_stats, store_from_file
from data_pipeline.ingestion.postgres_store import store_documents_from_file
from data_pipeline.processor.run_processing import process_raw_documents
from data_pipeline.scraper.indiankanoon_scraper import scrape_documents
from data_pipeline.utils import load_jsonl

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("run_pipeline")


def step_scrape(limit: int, settings: PipelineSettings) -> None:
    logger.info("=== STEP: SCRAPE (target=%s) ===", limit)
    path = scrape_documents(limit=limit, settings=settings)
    count = len(load_jsonl(path))
    logger.info("Raw documents on disk: %s", count)


def step_process() -> None:
    logger.info("=== STEP: PROCESS ===")
    processed_path, chunks_path = process_raw_documents()
    logger.info("Processed: %s | Chunks: %s", len(load_jsonl(processed_path)), len(load_jsonl(chunks_path)))


def step_ingest(
    settings: PipelineSettings,
    recreate: bool = False,
    ingest_target: str = "all",
) -> None:
    logger.info("=== STEP: INGEST (target=%s) ===", ingest_target)
    processed_path = PROCESSED_DIR / "documents.jsonl"
    chunks_path = CHUNKS_DIR / "chunks.jsonl"

    if not processed_path.exists() or not chunks_path.exists():
        raise FileNotFoundError("Processed data missing. Run --step process first.")

    pg_count = es_count = qdrant_count = None

    if ingest_target in ("all", "postgres"):
        pg_count = store_documents_from_file(processed_path, settings=settings)
        logger.info("PostgreSQL documents: %s", pg_count)

    if ingest_target in ("all", "elasticsearch"):
        es_count = index_from_files(
            chunks_path,
            processed_path,
            settings=settings,
            recreate_index=recreate,
        )
        logger.info("Elasticsearch chunks indexed: %s", es_count)

    if ingest_target in ("all", "qdrant"):
        qdrant_count = store_from_file(
            chunks_path,
            settings=settings,
            recreate_collection=recreate,
        )
        logger.info("Qdrant chunks stored: %s", qdrant_count)


def step_verify(settings: PipelineSettings) -> None:
    logger.info("=== STEP: VERIFY ===")
    processed_count = len(load_jsonl(PROCESSED_DIR / "documents.jsonl"))
    chunks_count = len(load_jsonl(CHUNKS_DIR / "chunks.jsonl"))
    es_stats = get_index_stats(settings)
    qdrant_stats = get_collection_stats(settings)

    logger.info("Processed documents (local): %s", processed_count)
    logger.info("Chunks (local): %s", chunks_count)
    logger.info("Elasticsearch: %s", es_stats)
    logger.info("Qdrant: %s", qdrant_stats)

    es_count = es_stats.get("count", 0)
    qdrant_points = qdrant_stats.get("points_count", 0)
    if processed_count == 0 or chunks_count == 0:
        raise RuntimeError("No processed data found.")
    if es_count == 0 or qdrant_points == 0:
        raise RuntimeError("Ingestion incomplete — ES or Qdrant has zero records.")


def main() -> None:
    parser = argparse.ArgumentParser(description="LexSearch data pipeline (Phase 2)")
    parser.add_argument(
        "--step",
        choices=["scrape", "process", "ingest", "verify", "all"],
        default="all",
        help="Pipeline step to run",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Number of judgements to scrape (default: SCRAPE_TARGET_COUNT env or 1000)",
    )
    parser.add_argument(
        "--recreate",
        action="store_true",
        help="Recreate Elasticsearch index and Qdrant collection before ingest",
    )
    parser.add_argument(
        "--ingest-target",
        choices=["all", "postgres", "elasticsearch", "qdrant"],
        default="all",
        help="Which ingest backends to run (default: all)",
    )
    args = parser.parse_args()

    ensure_data_dirs()
    settings = PipelineSettings.from_env()
    limit = args.limit or settings.scrape_target_count

    if args.step in ("scrape", "all"):
        step_scrape(limit=limit, settings=settings)

    if args.step in ("process", "all"):
        step_process()

    if args.step in ("ingest", "all"):
        step_ingest(
            settings=settings,
            recreate=args.recreate,
            ingest_target=args.ingest_target,
        )

    if args.step in ("verify", "all"):
        step_verify(settings=settings)

    logger.info("Pipeline step '%s' completed successfully.", args.step)


if __name__ == "__main__":
    main()
