from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date
from typing import Any


@dataclass
class RawDocument:
    id: str
    title: str
    full_text: str
    url: str
    court_hint: str | None = None
    raw_html_snippet: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RawDocument":
        return cls(**data)


@dataclass
class DocumentMetadata:
    court: str | None = None
    date: date | None = None
    case_type: str | None = None
    outcome: str | None = None
    judges: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        if self.date:
            result["date"] = self.date.isoformat()
        return result


@dataclass
class ProcessedDocument:
    id: str
    title: str
    full_text: str
    url: str
    court: str | None = None
    date: date | None = None
    case_type: str | None = None
    outcome: str | None = None
    judges: list[str] = field(default_factory=list)
    full_text_length: int = 0

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        if self.date:
            result["date"] = self.date.isoformat()
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProcessedDocument":
        date_value = data.get("date")
        parsed_date = date.fromisoformat(date_value) if date_value else None
        return cls(
            id=data["id"],
            title=data["title"],
            full_text=data["full_text"],
            url=data["url"],
            court=data.get("court"),
            date=parsed_date,
            case_type=data.get("case_type"),
            outcome=data.get("outcome"),
            judges=data.get("judges") or [],
            full_text_length=data.get("full_text_length") or len(data.get("full_text", "")),
        )


@dataclass
class DocumentChunk:
    document_id: str
    chunk_index: int
    text: str
    title: str
    court: str | None
    date: date | None
    case_type: str | None
    char_start: int
    char_end: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "document_id": self.document_id,
            "chunk_index": self.chunk_index,
            "text": self.text,
            "title": self.title,
            "court": self.court,
            "date": self.date.isoformat() if self.date else None,
            "case_type": self.case_type,
            "char_start": self.char_start,
            "char_end": self.char_end,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DocumentChunk":
        date_value = data.get("date")
        parsed_date = date.fromisoformat(date_value) if date_value else None
        return cls(
            document_id=data["document_id"],
            chunk_index=data["chunk_index"],
            text=data["text"],
            title=data["title"],
            court=data.get("court"),
            date=parsed_date,
            case_type=data.get("case_type"),
            char_start=data.get("char_start", 0),
            char_end=data.get("char_end", len(data.get("text", ""))),
        )
