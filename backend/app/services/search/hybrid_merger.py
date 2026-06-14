"""Reciprocal Rank Fusion (RRF) score merging."""

from __future__ import annotations

from app.services.search.filter_builder import RRF_K
from app.services.search.models import ChunkResult


def reciprocal_rank_fusion(
    result_lists: list[list[ChunkResult]],
    k: int = RRF_K,
) -> list[ChunkResult]:
    """
    RRF score = sum of 1/(rank + k) for each result's rank in each list.
    Default k=60 per architecture specification.
    """
    scores: dict[str, float] = {}
    chunks_by_key: dict[str, ChunkResult] = {}

    for results in result_lists:
        for rank, chunk in enumerate(results, start=1):
            key = chunk.chunk_key
            scores[key] = scores.get(key, 0.0) + 1.0 / (rank + k)
            if key not in chunks_by_key:
                chunks_by_key[key] = chunk

    ranked_keys = sorted(scores.keys(), key=lambda item: scores[item], reverse=True)

    merged: list[ChunkResult] = []
    for key in ranked_keys:
        chunk = chunks_by_key[key]
        merged.append(
            ChunkResult(
                document_id=chunk.document_id,
                chunk_index=chunk.chunk_index,
                text=chunk.text,
                title=chunk.title,
                court=chunk.court,
                date=chunk.date,
                case_type=chunk.case_type,
                score=scores[key],
            )
        )
    return merged
