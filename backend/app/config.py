from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(
            str(PROJECT_ROOT / ".env"),
            str(BACKEND_ROOT / ".env"),
            ".env",
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/lexsearch"
    redis_url: str = "redis://localhost:6379"
    jwt_secret_key: str = "dev-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 24
    elasticsearch_url: str = "http://localhost:9200"
    elasticsearch_index: str = "legal_judgements"
    elasticsearch_api_key: str | None = None
    elasticsearch_user: str | None = None
    elasticsearch_password: str | None = None
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None
    qdrant_collection_name: str = "legal_judgements"
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    groq_api_key: str | None = None
    gemini_api_key: str | None = None
    ollama_base_url: str = "http://localhost:11434"
    llm_primary_provider: str = "groq"
    llm_fallback_order: str = "groq,gemini"
    llm_timeout_seconds: int = 30
    groq_model: str = "llama-3.3-70b-versatile"
    gemini_model: str = "gemini-2.5-flash"
    ollama_model: str = "llama3.1"
    frontend_url: str = "http://localhost:3000"
    backend_url: str = "http://localhost:8000"
    environment: str = "development"
    search_cache_ttl_seconds: int = 3600
    document_summary_cache_ttl_seconds: int = 86400
    processed_documents_path: str = str(PROJECT_ROOT / "data_pipeline" / "data" / "processed" / "documents.jsonl")
    chunks_data_path: str = str(PROJECT_ROOT / "data_pipeline" / "data" / "chunks" / "chunks.jsonl")

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: object) -> object:
        """Railway/Heroku provide postgresql:// — async SQLAlchemy needs postgresql+asyncpg://."""
        if not isinstance(value, str):
            return value
        url = value.strip()
        if url.startswith("postgres://"):
            return "postgresql+asyncpg://" + url[len("postgres://") :]
        if url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
            return "postgresql+asyncpg://" + url[len("postgresql://") :]
        return url

    @property
    def qdrant_api_key_or_none(self) -> str | None:
        key = (self.qdrant_api_key or "").strip()
        return key or None

    @property
    def groq_api_key_or_none(self) -> str | None:
        key = (self.groq_api_key or "").strip()
        return key or None

    @property
    def gemini_api_key_or_none(self) -> str | None:
        key = (self.gemini_api_key or "").strip()
        return key or None

    @property
    def elasticsearch_api_key_or_none(self) -> str | None:
        key = (self.elasticsearch_api_key or "").strip()
        return key or None

    @property
    def elasticsearch_basic_auth(self) -> tuple[str, str] | None:
        user = (self.elasticsearch_user or "").strip()
        password = (self.elasticsearch_password or "").strip()
        if user and password:
            return user, password
        return None

    @property
    def llm_provider_order(self) -> list[str]:
        return [p.strip().lower() for p in self.llm_fallback_order.split(",") if p.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
