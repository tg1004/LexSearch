from app.services.rag.citation_parser import extract_citation_numbers, parse_citations
from app.services.search.models import ChunkResult


def _chunk(index: int) -> ChunkResult:
    return ChunkResult(
        document_id=f"doc-{index}",
        chunk_index=index,
        text=f"Passage text for chunk {index}",
        title=f"Case {index}",
        court="Supreme Court",
        date="2020-01-01",
        case_type="Criminal",
    )


def test_extract_bracket_and_paren_citations():
    text = "Privacy is fundamental [1] and bail may be granted (2). See Source 3."
    assert extract_citation_numbers(text) == [1, 2, 3]


def test_parse_citations_maps_to_chunks():
    chunks = [_chunk(0), _chunk(1)]
    parsed = parse_citations("The court held [1] and also noted (2).", chunks)
    assert len(parsed.citations) == 2
    assert parsed.citations[0].document_id == "doc-0"
    assert parsed.citations[1].number == 2
