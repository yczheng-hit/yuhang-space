"""体重相关 Pydantic 模型。"""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


class WeightProfileCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    color: str | None = None


class WeightProfileUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=50)
    color: str | None = None


class WeightProfileResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    color: str | None
    record_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WeightRecordCreate(BaseModel):
    weight: float = Field(..., gt=0, le=500)
    date: date
    note: str | None = Field(default=None, max_length=200)


class WeightRecordUpdate(BaseModel):
    weight: float | None = Field(default=None, gt=0, le=500)
    note: str | None = None


class WeightRecordResponse(BaseModel):
    id: uuid.UUID
    profile_id: uuid.UUID
    weight: float
    date: date
    note: str | None
    created_at: datetime

    model_config = {"from_attributes": True}