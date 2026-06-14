from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.history import SearchHistoryItem, SearchHistoryListResponse
from app.services.user import history_service
from app.utils.auth_utils import get_current_user

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("", response_model=SearchHistoryListResponse)
async def get_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SearchHistoryListResponse:
    items = await history_service.list_search_history(db, current_user.id)
    return SearchHistoryListResponse(
        items=[SearchHistoryItem.model_validate(item) for item in items],
        total=len(items),
    )


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def clear_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    await history_service.clear_search_history(db, current_user.id)


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_history_entry(
    entry_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    deleted = await history_service.delete_search_history_entry(db, current_user.id, entry_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="History entry not found")
