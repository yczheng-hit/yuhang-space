"""体重 ORM 模型 — 角色与记录。"""

import uuid
from datetime import UTC, date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


def _utcnow() -> datetime:
    return datetime.now(UTC)


class WeightProfile(Base):
    __tablename__ = "weight_profiles"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid(), ForeignKey("users.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    color: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow)

    records: Mapped[list] = relationship("WeightRecord", back_populates="profile", cascade="all, delete-orphan")


class WeightRecord(Base):
    __tablename__ = "weight_records"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True, default=uuid.uuid4)
    profile_id: Mapped[uuid.UUID] = mapped_column(Uuid(), ForeignKey("weight_profiles.id"), nullable=False, index=True)
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    note: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow)

    profile: Mapped[WeightProfile] = relationship("WeightProfile", back_populates="records")