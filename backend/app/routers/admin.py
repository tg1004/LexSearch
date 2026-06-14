from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.admin import AdminStatsResponse
from app.services.user import admin_service
from app.utils.auth_utils import get_admin_user

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/stats", response_model=AdminStatsResponse)
async def get_stats(
    _: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
) -> AdminStatsResponse:
    return await admin_service.get_admin_stats(db)
