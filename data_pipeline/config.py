import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PIPELINE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = PIPELINE_ROOT.parent
DATA_DIR = PIPELINE_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
CHUNKS_DIR = DATA_DIR / "chunks"

load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(PIPELINE_ROOT / ".env")


@dataclass(frozen=True)
class PipelineSettings:
    database_url: str
    elasticsearch_url: str
    elasticsearch_index: str
    elasticsearch_api_key: str | None
    elasticsearch_user: str | None
    elasticsearch_password: str | None
    qdrant_url: str
    qdrant_api_key: str | None
    qdrant_collection_name: str
    embedding_model: str
    embedding_dimension: int
    scrape_target_count: int
    scrape_delay_seconds: float
    scrape_timeout_seconds: int
    indiankanoon_base_url: str

    @classmethod
    def from_env(cls) -> "PipelineSettings":
        db_url = os.getenv(
            "DATABASE_URL",
            "postgresql+asyncpg://postgres:password@localhost:5432/lexsearch",
        )
        # Pipeline uses sync psycopg2 driver
        sync_db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")

        return cls(
            database_url=sync_db_url,
            elasticsearch_url=os.getenv("ELASTICSEARCH_URL", "http://localhost:9200"),
            elasticsearch_index=os.getenv("ELASTICSEARCH_INDEX", "legal_judgements"),
            elasticsearch_api_key=(os.getenv("ELASTICSEARCH_API_KEY") or "").strip() or None,
            elasticsearch_user=(os.getenv("ELASTICSEARCH_USER") or "").strip() or None,
            elasticsearch_password=(os.getenv("ELASTICSEARCH_PASSWORD") or "").strip() or None,
            qdrant_url=os.getenv("QDRANT_URL", "http://localhost:6333"),
            qdrant_api_key=(os.getenv("QDRANT_API_KEY") or "").strip() or None,
            qdrant_collection_name=os.getenv("QDRANT_COLLECTION_NAME", "legal_judgements"),
            embedding_model=os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
            embedding_dimension=int(os.getenv("EMBEDDING_DIMENSION", "384")),
            scrape_target_count=int(os.getenv("SCRAPE_TARGET_COUNT", "1000")),
            scrape_delay_seconds=float(os.getenv("SCRAPE_DELAY_SECONDS", "1.5")),
            scrape_timeout_seconds=int(os.getenv("SCRAPE_TIMEOUT_SECONDS", "30")),
            indiankanoon_base_url=os.getenv("INDIANKANOON_BASE_URL", "https://indiankanoon.org"),
        )


def ensure_data_dirs() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
