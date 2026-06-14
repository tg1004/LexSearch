from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.feedback import Feedback
from app.models.search_history import SearchHistory
from app.schemas.admin import (
    AdminStatsResponse,
    DailySearchCount,
    FailedQueryItem,
    FeedbackSummary,
    NegativeFeedbackItem,
    ProviderCount,
    TopSearchTerm,
)


async def get_admin_stats(db: AsyncSession) -> AdminStatsResponse:
    now = datetime.now(UTC)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=today_start.weekday())
    thirty_days_ago = today_start - timedelta(days=29)

    searches_today = await db.scalar(
        select(func.count()).select_from(SearchHistory).where(SearchHistory.searched_at >= today_start)
    )
    searches_this_week = await db.scalar(
        select(func.count()).select_from(SearchHistory).where(SearchHistory.searched_at >= week_start)
    )

    provider_rows = (
        await db.execute(
            select(SearchHistory.provider_used, func.count())
            .where(SearchHistory.searched_at >= thirty_days_ago)
            .where(SearchHistory.provider_used.isnot(None))
            .group_by(SearchHistory.provider_used)
            .order_by(func.count().desc())
        )
    ).all()
    provider_distribution = [
        ProviderCount(provider=row[0] or "unknown", count=row[1]) for row in provider_rows
    ]

    day_expr = func.date(SearchHistory.searched_at)
    daily_rows = (
        await db.execute(
            select(day_expr, func.count())
            .where(SearchHistory.searched_at >= thirty_days_ago)
            .group_by(day_expr)
            .order_by(day_expr.asc())
        )
    ).all()
    searches_per_day = [DailySearchCount(date=row[0], count=row[1]) for row in daily_rows]

    top_rows = (
        await db.execute(
            select(SearchHistory.query, func.count())
            .where(SearchHistory.searched_at >= thirty_days_ago)
            .group_by(SearchHistory.query)
            .order_by(func.count().desc())
            .limit(10)
        )
    ).all()
    top_search_terms = [TopSearchTerm(term=row[0], count=row[1]) for row in top_rows]

    helpful_count = await db.scalar(
        select(func.count()).select_from(Feedback).where(Feedback.is_helpful.is_(True))
    )
    not_helpful_count = await db.scalar(
        select(func.count()).select_from(Feedback).where(Feedback.is_helpful.is_(False))
    )
    helpful_count = helpful_count or 0
    not_helpful_count = not_helpful_count or 0
    total_feedback = helpful_count + not_helpful_count
    helpful_percent = round((helpful_count / total_feedback) * 100, 1) if total_feedback else 0.0

    negative_rows = (
        await db.execute(
            select(Feedback.query, Feedback.provider_used, Feedback.created_at)
            .where(Feedback.is_helpful.is_(False))
            .order_by(Feedback.created_at.desc())
            .limit(20)
        )
    ).all()
    recent_negative_feedback = [
        NegativeFeedbackItem(
            query=row[0],
            provider_used=row[1],
            created_at=row[2],
        )
        for row in negative_rows
    ]

    failed_rows = (
        await db.execute(
            select(SearchHistory.query, SearchHistory.searched_at)
            .where(
                SearchHistory.result_count == 0,
                SearchHistory.searched_at >= thirty_days_ago,
            )
            .order_by(SearchHistory.searched_at.desc())
            .limit(20)
        )
    ).all()
    recent_failed_queries = [
        FailedQueryItem(query=row[0], failed_at=row[1]) for row in failed_rows
    ]

    return AdminStatsResponse(
        searches_today=searches_today or 0,
        searches_this_week=searches_this_week or 0,
        avg_response_time_ms=None,
        provider_distribution=provider_distribution,
        searches_per_day=searches_per_day,
        top_search_terms=top_search_terms,
        feedback_summary=FeedbackSummary(
            helpful=helpful_count,
            not_helpful=not_helpful_count,
            helpful_percent=helpful_percent,
        ),
        recent_negative_feedback=recent_negative_feedback,
        recent_failed_queries=recent_failed_queries,
    )
