"""体重路由 — 角色与记录 CRUD。"""

import uuid

from fastapi import APIRouter, Query

from app.dependencies import CurrentUser, DBSession
from app.schemas.weight import (
    WeightProfileCreate,
    WeightProfileResponse,
    WeightProfileUpdate,
    WeightRecordCreate,
    WeightRecordResponse,
    WeightRecordUpdate,
)
from app.services import weight_service

router = APIRouter()


@router.post("/profiles", response_model=WeightProfileResponse)
async def create_profile(data: WeightProfileCreate, db: DBSession, user: CurrentUser):
    """创建体重角色。"""
    profile = await weight_service.create_profile(db, user.id, data)
    return {**{c.name: getattr(profile, c.name) for c in profile.__table__.columns}, "record_count": 0}


@router.get("/profiles", response_model=list[WeightProfileResponse])
async def list_profiles(db: DBSession, user: CurrentUser):
    """列出当前用户的所有角色。"""
    return await weight_service.list_profiles(db, user.id)


@router.patch("/profiles/{profile_id}", response_model=WeightProfileResponse)
async def update_profile(
    profile_id: uuid.UUID, data: WeightProfileUpdate, db: DBSession, user: CurrentUser
):
    """更新角色。"""
    profile = await weight_service.update_profile(db, profile_id, user.id, data)
    return {**{c.name: getattr(profile, c.name) for c in profile.__table__.columns}, "record_count": 0}


@router.delete("/profiles/{profile_id}")
async def delete_profile(profile_id: uuid.UUID, db: DBSession, user: CurrentUser):
    """删除角色。"""
    await weight_service.delete_profile(db, profile_id, user.id)
    return {"detail": "已删除"}


@router.post("/profiles/{profile_id}/records", response_model=WeightRecordResponse)
async def create_record(
    profile_id: uuid.UUID, data: WeightRecordCreate, db: DBSession, user: CurrentUser
):
    """添加体重记录。"""
    return await weight_service.create_record(db, profile_id, user.id, data)


@router.get("/profiles/{profile_id}/records", response_model=list[WeightRecordResponse])
async def list_records(
    profile_id: uuid.UUID,
    db: DBSession,
    user: CurrentUser,
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
):
    """列出某角色的体重记录。"""
    return await weight_service.list_records(db, profile_id, user.id, date_from, date_to)


@router.patch("/records/{record_id}", response_model=WeightRecordResponse)
async def update_record(
    record_id: uuid.UUID, data: WeightRecordUpdate, db: DBSession, user: CurrentUser
):
    """更新记录。"""
    return await weight_service.update_record(db, record_id, user.id, data)


@router.delete("/records/{record_id}")
async def delete_record(record_id: uuid.UUID, db: DBSession, user: CurrentUser):
    """删除记录。"""
    await weight_service.delete_record(db, record_id, user.id)
    return {"detail": "已删除"}