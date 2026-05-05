"""日程路由 — CRUD + 媒体上传。"""

import uuid

from fastapi import APIRouter, UploadFile, File

from app.dependencies import CurrentUser, DBSession
from app.schemas.schedule import ScheduleCreate, ScheduleResponse, ScheduleUpdate
from app.services import media_service, schedule_service

router = APIRouter()


@router.post("", response_model=ScheduleResponse)
async def create(data: ScheduleCreate, db: DBSession, user: CurrentUser):
    """创建日程。"""
    schedule = await schedule_service.create_schedule(db, user.id, data)
    return schedule


@router.get("", response_model=list[ScheduleResponse])
async def list_all(
    db: DBSession,
    user: CurrentUser,
    skip: int = 0,
    limit: int = 50,
):
    """列出当前用户的所有日程。"""
    return await schedule_service.list_schedules(db, user.id, skip, limit)


@router.get("/{schedule_id}", response_model=ScheduleResponse)
async def get_one(schedule_id: uuid.UUID, db: DBSession, user: CurrentUser):
    """获取单个日程。"""
    return await schedule_service.get_schedule(db, schedule_id, user.id)


@router.patch("/{schedule_id}", response_model=ScheduleResponse)
async def update(
    schedule_id: uuid.UUID,
    data: ScheduleUpdate,
    db: DBSession,
    user: CurrentUser,
):
    """更新日程。"""
    return await schedule_service.update_schedule(db, schedule_id, user.id, data)


@router.delete("/{schedule_id}")
async def delete(schedule_id: uuid.UUID, db: DBSession, user: CurrentUser):
    """删除日程。"""
    await schedule_service.delete_schedule(db, schedule_id, user.id)
    return {"detail": "已删除"}


@router.post("/{schedule_id}/media")
async def upload_media(
    schedule_id: uuid.UUID,
    file: UploadFile = File(...),
    db: DBSession = None,
    user: CurrentUser = None,
):
    """为日程上传媒体文件。"""
    media = await media_service.upload_media(db, user.id, file, schedule_id=schedule_id)
    return {"id": media.id, "file_path": media.file_path, "file_type": media.file_type}


@router.get("/{schedule_id}/media")
async def list_media(schedule_id: uuid.UUID, db: DBSession, user: CurrentUser):
    """列出日程的所有媒体文件。"""
    return await media_service.get_media_by_schedule(db, schedule_id)
