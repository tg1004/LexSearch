from datetime import date, datetime

from pydantic import BaseModel


class DailySearchCount(BaseModel):
    date: date
    count: int


class TopSearchTerm(BaseModel):
    term: str
    count: int


class ProviderCount(BaseModel):
    provider: str
    count: int


class FeedbackSummary(BaseModel):
    helpful: int
    not_helpful: int
    helpful_percent: float


class NegativeFeedbackItem(BaseModel):
    query: str
    provider_used: str | None = None
    created_at: datetime


class FailedQueryItem(BaseModel):
    query: str
    failed_at: datetime


class AdminStatsResponse(BaseModel):
    searches_today: int
    searches_this_week: int
    avg_response_time_ms: float | None = None
    provider_distribution: list[ProviderCount]
    searches_per_day: list[DailySearchCount]
    top_search_terms: list[TopSearchTerm]
    feedback_summary: FeedbackSummary
    recent_negative_feedback: list[NegativeFeedbackItem]
    recent_failed_queries: list[FailedQueryItem]
