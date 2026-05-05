"""运维路由 — 健康检查、统计、清理。"""

from pathlib import Path

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.models.media import MediaFile
from app.models.recipe import Recipe
from app.models.schedule import Schedule
from app.models.user import User
from app.schemas.maintenance import CleanupResponse, HealthResponse, StatsResponse
from app.security.maintenance_auth import verify_maintenance_auth

router = APIRouter(dependencies=[Depends(verify_maintenance_auth)])


@router.get("/health", response_model=HealthResponse)
async def health():
    """健康检查。"""
    return HealthResponse()


@router.get("/stats", response_model=StatsResponse)
async def stats(db: AsyncSession = Depends(get_async_session)):
    """数据库统计。"""
    users_count = (await db.execute(select(func.count(User.id)))).scalar() or 0
    schedules_count = (await db.execute(select(func.count(Schedule.id)))).scalar() or 0
    recipes_count = (await db.execute(select(func.count(Recipe.id)))).scalar() or 0
    media_count = (await db.execute(select(func.count(MediaFile.id)))).scalar() or 0

    return StatsResponse(
        total_users=users_count,
        total_schedules=schedules_count,
        total_recipes=recipes_count,
        total_media_files=media_count,
    )


@router.post("/cleanup-orphaned-media", response_model=CleanupResponse)
async def cleanup_orphaned_media(db: AsyncSession = Depends(get_async_session)):
    """清理孤立媒体文件（数据库记录存在但磁盘文件已丢失）。"""
    from app.config import settings

    result = await db.execute(select(MediaFile))
    media_files = result.scalars().all()

    deleted_count = 0
    for media in media_files:
        full_path = settings.media_root_path / media.file_path
        if not full_path.exists():
            await db.delete(media)
            deleted_count += 1

    await db.commit()
    return CleanupResponse(
        deleted_count=deleted_count,
        message=f"已清理 {deleted_count} 条孤立媒体记录",
    )
