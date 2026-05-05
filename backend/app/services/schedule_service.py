"""日程业务逻辑。"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.schedule import Schedule
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate


async def create_schedule(
    db: AsyncSession, user_id: uuid.UUID, data: ScheduleCreate
) -> Schedule:
    """创建日程。"""
    schedule = Schedule(user_id=user_id, **data.model_dump())
    db.add(schedule)
    await db.commit()
    await db.refresh(schedule)
    return schedule


async def get_schedule(
    db: AsyncSession, schedule_id: uuid.UUID, user_id: uuid.UUID
) -> Schedule:
    """获取单个日程（校验所有权）。"""
    result = await db.execute(
        select(Schedule).where(Schedule.id == schedule_id, Schedule.user_id == user_id)
    )
    schedule = result.scalar_one_or_none()
    if schedule is None:
        raise NotFoundException("日程不存在")
    return schedule


async def list_schedules(
    db: AsyncSession, user_id: uuid.UUID, skip: int = 0, limit: int = 50
) -> list[Schedule]:
    """列出用户的所有日程。"""
    result = await db.execute(
        select(Schedule)
        .where(Schedule.user_id == user_id)
        .order_by(Schedule.start_time.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def update_schedule(
    db: AsyncSession, schedule_id: uuid.UUID, user_id: uuid.UUID, data: ScheduleUpdate
) -> Schedule:
    """更新日程。"""
    schedule = await get_schedule(db, schedule_id, user_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(schedule, field, value)
    await db.commit()
    await db.refresh(schedule)
    return schedule


async def delete_schedule(
    db: AsyncSession, schedule_id: uuid.UUID, user_id: uuid.UUID
) -> None:
    """删除日程。"""
    schedule = await get_schedule(db, schedule_id, user_id)
    await db.delete(schedule)
    await db.commit()
