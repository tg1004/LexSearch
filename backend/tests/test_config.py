"""Tests for production environment configuration."""

from app.config import Settings


def test_normalizes_railway_postgresql_url():
    settings = Settings(database_url="postgresql://user:pass@host:5432/railway")
    assert settings.database_url == "postgresql+asyncpg://user:pass@host:5432/railway"


def test_normalizes_postgres_scheme():
    settings = Settings(database_url="postgres://user:pass@host:5432/db")
    assert settings.database_url == "postgresql+asyncpg://user:pass@host:5432/db"


def test_preserves_asyncpg_url():
    url = "postgresql+asyncpg://postgres:password@localhost:5432/lexsearch"
    settings = Settings(database_url=url)
    assert settings.database_url == url


def test_strips_trailing_slash_from_frontend_url():
    settings = Settings(frontend_url="https://lex-search-ten.vercel.app/")
    assert settings.frontend_url == "https://lex-search-ten.vercel.app"
    assert "https://lex-search-ten.vercel.app" in settings.cors_origins
