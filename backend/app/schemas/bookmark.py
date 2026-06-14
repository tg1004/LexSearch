from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class BookmarkCreate(BaseModel):
    document_id: str = Field(min_length=1, max_length=100)
    folder_name: str = Field(default="General", min_length=1, max_length=100)
    notes: str | None = Field(default=None, max_length=2000)


class BookmarkUpdate(BaseModel):
    folder_name: str | None = Field(default=None, min_length=1, max_length=100)
    notes: str | None = Field(default=None, max_length=2000)


class BookmarkResponse(BaseModel):
    id: UUID
    document_id: str | None
    folder_name: str
    notes: str | None = None
    created_at: datetime
    title: str | None = None
    court: str | None = None
    date: str | None = None

    model_config = {"from_attributes": True}


class BookmarkListResponse(BaseModel):
    items: list[BookmarkResponse]
    folders: list[str]
