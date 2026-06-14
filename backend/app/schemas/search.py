from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

MIN_YEAR = 1950
MAX_YEAR = 2100


class SearchFilters(BaseModel):
    court: list[str] = Field(default_factory=list, max_length=20)
    year_from: int | None = Field(default=None, ge=MIN_YEAR, le=MAX_YEAR)
    year_to: int | None = Field(default=None, ge=MIN_YEAR, le=MAX_YEAR)
    case_type: list[str] = Field(default_factory=list, max_length=20)
    outcome: list[str] = Field(default_factory=list, max_length=10)

    @field_validator("year_from", "year_to", mode="before")
    @classmethod
    def empty_year_to_none(cls, value: object) -> object:
        # Swagger UI sends 0 for unset integer fields — treat as no filter.
        if value in (0, "0", ""):
            return None
        return value

    @model_validator(mode="after")
    def sort_year_bounds(self) -> "SearchFilters":
        if self.year_from is not None and self.year_to is not None and self.year_from > self.year_to:
            self.year_from, self.year_to = self.year_to, self.year_from
        return self


ALLOWED_PROVIDERS = frozenset({"auto", "groq", "gemini", "ollama"})


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    preferred_provider: str | None = None
    filters: SearchFilters = Field(default_factory=SearchFilters)
    page: int = Field(default=1, ge=1, le=100)

    @field_validator("preferred_provider", mode="before")
    @classmethod
    def normalize_provider(cls, value: object) -> object:
        if value is None or (isinstance(value, str) and not value.strip()):
            return "auto"
        return value

    @field_validator("preferred_provider")
    @classmethod
    def validate_provider(cls, value: str | None) -> str | None:
        if value is not None and value.lower() not in ALLOWED_PROVIDERS:
            raise ValueError(f"preferred_provider must be one of: {', '.join(sorted(ALLOWED_PROVIDERS))}")
        return value.lower() if value else "auto"


class CitationResult(BaseModel):
    number: int
    document_id: str
    passage: str
    title: str
    court: str | None = None
    date: str | None = None


class SourceResult(BaseModel):
    document_id: str
    title: str
    court: str | None = None
    date: str | None = None
    snippet: str
    score: float
    chunk_index: int | None = None


class SearchResponse(BaseModel):
    answer: str = ""
    citations: list[CitationResult] = Field(default_factory=list)
    sources: list[SourceResult] = Field(default_factory=list)
    provider_used: str | None = None
    related_questions: list[str] = Field(default_factory=list)
    search_id: UUID
    result_count: int = 0
