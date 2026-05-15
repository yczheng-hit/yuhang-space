"""体重业务逻辑 — 角色与记录 CRUD。"""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.weight import WeightProfile, WeightRecord
from app.schemas.weight import WeightProfileCreate, WeightProfileUpdate, WeightRecordCreate, WeightRecordUpdate


async def create_profile(
    db: AsyncSession, user_id: uuid.UUID, data: WeightProfileCreate
) -> WeightProfile:
    """创建体重角色。"""
    profile = WeightProfile(user_id=user_id, **data.model_dump())
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile


async def list_profiles(db: AsyncSession, user_id: uuid.UUID) -> list[dict]:
    """列出用户的所有角色（含记录数）。"""
    result = await db.execute(
        select(
            WeightProfile,
            func.count(WeightRecord.id).label("record_count"),
        )
        .outerjoin(WeightRecord, WeightRecord.profile_id == WeightProfile.id)
        .where(WeightProfile.user_id == user_id)
        .group_by(WeightProfile.id)
        .order_by(WeightProfile.created_at)
    )
    rows = result.all()
    profiles = []
    for profile, count in rows:
        d = {c.name: getattr(profile, c.name) for c in profile.__table__.columns}
        d["record_count"] = count
        profiles.append(d)
    return profiles


async def get_profile(db: AsyncSession, profile_id: uuid.UUID, user_id: uuid.UUID) -> WeightProfile:
    """获取单个角色（校验所有权）。"""
    result = await db.execute(
        select(WeightProfile).where(WeightProfile.id == profile_id, WeightProfile.user_id == user_id)
    )
    profile = result.scalar_one_or_none()
    if profile is None:
        raise NotFoundException("角色不存在")
    return profile


async def update_profile(
    db: AsyncSession, profile_id: uuid.UUID, user_id: uuid.UUID, data: WeightProfileUpdate
) -> WeightProfile:
    """更新角色。"""
    profile = await get_profile(db, profile_id, user_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    await db.commit()
    await db.refresh(profile)
    return profile


async def delete_profile(db: AsyncSession, profile_id: uuid.UUID, user_id: uuid.UUID) -> None:
    """删除角色（级联删除记录）。"""
    profile = await get_profile(db, profile_id, user_id)
    await db.delete(profile)
    await db.commit()


async def create_record(
    db: AsyncSession, profile_id: uuid.UUID, user_id: uuid.UUID, data: WeightRecordCreate
) -> WeightRecord:
    """创建体重记录（校验角色所有权）。"""
    await get_profile(db, profile_id, user_id)
    record = WeightRecord(profile_id=profile_id, **data.model_dump())
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


async def list_records(
    db: AsyncSession, profile_id: uuid.UUID, user_id: uuid.UUID,
    date_from: str | None = None, date_to: str | None = None,
) -> list[WeightRecord]:
    """列出某角色的体重记录。"""
    await get_profile(db, profile_id, user_id)
    query = select(WeightRecord).where(WeightRecord.profile_id == profile_id)
    if date_from:
        query = query.where(WeightRecord.date >= date_from)
    if date_to:
        query = query.where(WeightRecord.date <= date_to)
    query = query.order_by(WeightRecord.date.desc())
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_record(db: AsyncSession, record_id: uuid.UUID) -> WeightRecord:
    """获取单条记录。"""
    result = await db.execute(select(WeightRecord).where(WeightRecord.id == record_id))
    record = result.scalar_one_or_none()
    if record is None:
        raise NotFoundException("记录不存在")
    return record


async def update_record(
    db: AsyncSession, record_id: uuid.UUID, user_id: uuid.UUID, data: WeightRecordUpdate
) -> WeightRecord:
    """更新记录（校验角色所有权）。"""
    record = await get_record(db, record_id)
    await get_profile(db, record.profile_id, user_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(record, field, value)
    await db.commit()
    await db.refresh(record)
    return record


async def delete_record(db: AsyncSession, record_id: uuid.UUID, user_id: uuid.UUID) -> None:
    """删除记录（校验角色所有权）。"""
    record = await get_record(db, record_id)
    await get_profile(db, record.profile_id, user_id)
    await db.delete(record)
    await db.commit()