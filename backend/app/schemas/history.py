from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class SearchHistoryItem(BaseModel):
    id: UUID
    query: str
    provider_used: str | None = None
    result_count: int | None = None
    searched_at: datetime

    model_config = {"from_attributes": True}


class SearchHistoryListResponse(BaseModel):
    items: list[SearchHistoryItem]
    total: int
