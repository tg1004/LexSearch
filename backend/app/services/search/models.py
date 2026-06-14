from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ChunkResult:
    document_id: str
    chunk_index: int
    text: str
    title: str
    court: str | None
    date: str | None
    case_type: str | None
    score: float = 0.0

    @property
    def chunk_key(self) -> str:
        return f"{self.document_id}_{self.chunk_index}"
