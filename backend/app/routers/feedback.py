from fastapi import APIRouter, BackgroundTasks, Depends
from app.models.user import User
from app.schemas.feedback import FeedbackCreate, FeedbackResponse
from app.services.user import feedback_service
from app.utils.auth_utils import get_current_user, get_optional_user

router = APIRouter(prefix="/api/feedback", tags=["feedback"])


async def _persist_feedback(
    query: str,
    is_helpful: bool,
    provider_used: str | None,
    user_id,
) -> None:
    async with AsyncSessionLocal() as session:
        try:
            await feedback_service.create_feedback(
                session,
                query=query,
                is_helpful=is_helpful,
                provider_used=provider_used,
                user_id=user_id,
            )
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@router.post("", response_model=FeedbackResponse, status_code=201)
async def submit_feedback(
    body: FeedbackCreate,
    background_tasks: BackgroundTasks,
    current_user: User | None = Depends(get_optional_user),
) -> FeedbackResponse:
    background_tasks.add_task(
        _persist_feedback,
        body.query,
        body.is_helpful,
        body.provider_used,
        current_user.id if current_user else None,
    )
    return FeedbackResponse()
