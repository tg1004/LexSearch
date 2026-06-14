from __future__ import annotations

import re
from dataclasses import dataclass

from app.schemas.search import CitationResult
from app.services.search.models import ChunkResult

# [1], (1), Source 1, source 1, Ref. 1, etc.
CITATION_PATTERNS = [
    re.compile(r"\[(\d+)\]"),
    re.compile(r"\((\d+)\)"),
    re.compile(r"(?:Source|source|Ref\.?|ref\.?)\s*(\d+)\b"),
]


@dataclass
class ParsedAnswer:
    answer_text: str
    citations: list[CitationResult]


def extract_citation_numbers(text: str) -> list[int]:
    found: set[int] = set()
    for pattern in CITATION_PATTERNS:
        for match in pattern.finditer(text):
            number = int(match.group(1))
            if number > 0:
                found.add(number)
    return sorted(found)


def parse_citations(llm_response: str, chunks: list[ChunkResult]) -> ParsedAnswer:
    answer_text = llm_response.strip()
    referenced_numbers = extract_citation_numbers(answer_text)

    citations: list[CitationResult] = []
    for number in referenced_numbers:
        index = number - 1
        if index < 0 or index >= len(chunks):
            continue
        chunk = chunks[index]
        passage = chunk.text[:500] + ("..." if len(chunk.text) > 500 else "")
        citations.append(
            CitationResult(
                number=number,
                document_id=chunk.document_id,
                passage=passage,
                title=chunk.title,
                court=chunk.court,
                date=chunk.date,
            )
        )

    return ParsedAnswer(answer_text=answer_text, citations=citations)
