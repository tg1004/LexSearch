from datetime import date as DateType

from pydantic import BaseModel, Field


class DocumentResponse(BaseModel):
    id: str
    title: str
    court: str | None = None
    date: DateType | None = None
    judges: list[str] = Field(default_factory=list)
    case_type: str | None = None
    outcome: str | None = None
    bench_size: str | None = None
    full_text: str
    summary: str | None = None
    url: str | None = None

    model_config = {"from_attributes": True}


class DocumentSummaryResponse(BaseModel):
    document_id: str
    summary: str
    provider_used: str | None = None


class HighlightResponse(BaseModel):
    document_id: str
    chunk_index: int
    highlighted_passage: str
    position: int
    char_end: int
