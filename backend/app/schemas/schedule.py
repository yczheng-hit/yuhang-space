"""日程相关 Pydantic 模型。"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ScheduleCreate(BaseModel):
    title: str = Field(..., max_length=200)
    description: str | None = None
    start_time: datetime
    end_time: datetime | None = None
    priority: int = Field(default=0, ge=0, le=2)
    status: str = Field(default="pending")
    recurrence_rule: str | None = None
    tags: list[str] = []
    ai_generated: bool = False


class ScheduleUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    description: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    priority: int | None = Field(default=None, ge=0, le=2)
    status: str | None = None
    recurrence_rule: str | None = None
    tags: list[str] | None = None


class ScheduleResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    description: str | None
    start_time: datetime
    end_time: datetime | None
    priority: int
    status: str
    recurrence_rule: str | None
    tags: list[str]
    ai_generated: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
