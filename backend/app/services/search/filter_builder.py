"""Build Qdrant and Elasticsearch filters from SearchFilters."""

from __future__ import annotations

from typing import Any

from qdrant_client import models as qmodels

from app.schemas.search import SearchFilters

RRF_K = 60
VECTOR_TOP_K = 20
KEYWORD_TOP_K = 20
RESULTS_PER_PAGE = 10
RAG_TOP_K = 10
MAX_RETRIEVE_K = 100
MAX_SEARCH_PAGE = 100
MIN_YEAR = 1950
MAX_YEAR = 2100


def normalize_year(value: int | None) -> int | None:
    """Treat 0/invalid years as unset (Swagger often sends 0 for empty int fields)."""
    if value is None or value < MIN_YEAR or value > MAX_YEAR:
        return None
    return value


def normalized_year_bounds(filters: SearchFilters) -> tuple[int | None, int | None]:
    year_from = normalize_year(filters.year_from)
    year_to = normalize_year(filters.year_to)
    if year_from is not None and year_to is not None and year_from > year_to:
        year_from, year_to = year_to, year_from
    return year_from, year_to


def matches_year_filter(date_value: str | None, year_from: int | None, year_to: int | None) -> bool:
    """Post-filter for Qdrant results where date is stored as an ISO string payload."""
    if year_from is None and year_to is None:
        return True
    if not date_value:
        return False
    try:
        year = int(str(date_value)[:4])
    except ValueError:
        return False
    if year_from is not None and year < year_from:
        return False
    if year_to is not None and year > year_to:
        return False
    return True


def build_qdrant_filter(filters: SearchFilters) -> qmodels.Filter | None:
    """
    Build Qdrant filter for court and case_type.
    Year filtering is applied post-search because dates are ISO strings in payload.
    """
    conditions: list[qmodels.Condition] = []

    if filters.court:
        conditions.append(
            qmodels.FieldCondition(key="court", match=qmodels.MatchAny(any=filters.court))
        )

    if filters.case_type:
        conditions.append(
            qmodels.FieldCondition(key="case_type", match=qmodels.MatchAny(any=filters.case_type))
        )

    if filters.outcome:
        conditions.append(
            qmodels.FieldCondition(key="outcome", match=qmodels.MatchAny(any=filters.outcome))
        )

    if not conditions:
        return None
    return qmodels.Filter(must=conditions)


def build_elasticsearch_filters(filters: SearchFilters) -> list[dict[str, Any]]:
    es_filters: list[dict[str, Any]] = []

    if filters.court:
        es_filters.append({"terms": {"court": filters.court}})

    if filters.case_type:
        es_filters.append({"terms": {"case_type": filters.case_type}})

    if filters.outcome:
        es_filters.append({"terms": {"outcome": filters.outcome}})

    year_from, year_to = normalized_year_bounds(filters)
    if year_from is not None or year_to is not None:
        date_range: dict[str, str] = {}
        if year_from is not None:
            date_range["gte"] = f"{year_from}-01-01"
        if year_to is not None:
            date_range["lte"] = f"{year_to}-12-31"
        es_filters.append({"range": {"date": date_range}})

    return es_filters
