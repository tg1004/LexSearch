from app.schemas.search import SearchFilters
from app.services.search.filter_builder import (
    build_elasticsearch_filters,
    matches_year_filter,
    normalize_year,
    normalized_year_bounds,
)


def test_normalize_year_rejects_zero():
    assert normalize_year(0) is None
    assert normalize_year(2015) == 2015


def test_normalized_year_bounds_swaps_inverted_range():
    filters = SearchFilters(year_from=2024, year_to=2015)
    year_from, year_to = normalized_year_bounds(filters)
    assert year_from == 2015
    assert year_to == 2024


def test_elasticsearch_filter_skips_invalid_years():
    filters = SearchFilters(year_from=0, year_to=0)
    assert build_elasticsearch_filters(filters) == []


def test_build_qdrant_filter_includes_outcome():
    from app.services.search.filter_builder import build_qdrant_filter

    filters = SearchFilters(outcome=["Allowed", "Dismissed"])
    qfilter = build_qdrant_filter(filters)
    assert qfilter is not None
    assert len(qfilter.must) == 1


def test_matches_year_filter():
    assert matches_year_filter("2017-08-24", 2015, 2020) is True
    assert matches_year_filter("2010-01-01", 2015, 2020) is False
    assert matches_year_filter(None, 2015, 2020) is False
    assert matches_year_filter("2017-08-24", None, None) is True
