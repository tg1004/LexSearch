from pydantic import BaseModel, Field


class FeedbackCreate(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    is_helpful: bool
    provider_used: str | None = Field(default=None, max_length=50)
    search_id: str | None = Field(default=None, max_length=100)


class FeedbackResponse(BaseModel):
    message: str = "Feedback recorded"
