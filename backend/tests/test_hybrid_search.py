from app.services.search.hybrid_merger import reciprocal_rank_fusion
from app.services.search.models import ChunkResult


def _chunk(doc_id: str, index: int) -> ChunkResult:
    return ChunkResult(
        document_id=doc_id,
        chunk_index=index,
        text=f"text {doc_id}-{index}",
        title=f"Title {doc_id}",
        court="Supreme Court",
        date="2020-01-01",
        case_type="Criminal",
    )


def test_rrf_merges_overlapping_results():
    vector = [_chunk("1", 0), _chunk("2", 0), _chunk("3", 0)]
    keyword = [_chunk("2", 0), _chunk("4", 0), _chunk("1", 0)]

    merged = reciprocal_rank_fusion([vector, keyword], k=60)

    keys = [chunk.chunk_key for chunk in merged]
    assert keys[0] == "2_0"  # appears rank 2 in vector, rank 1 in keyword
    assert "1_0" in keys
    assert "4_0" in keys
    assert merged[0].score > merged[-1].score


def test_rrf_formula_k60():
    """Chunk at rank 1 in one list gets score 1/(1+60)."""
    merged = reciprocal_rank_fusion([[_chunk("9", 0)]], k=60)
    assert abs(merged[0].score - (1 / 61)) < 1e-9


def test_rrf_combines_both_lists():
    """Chunk at rank 1 in both lists gets 2/(61)."""
    chunk = _chunk("5", 0)
    merged = reciprocal_rank_fusion([[chunk], [chunk]], k=60)
    assert abs(merged[0].score - (2 / 61)) < 1e-9
