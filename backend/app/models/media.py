"""媒体文件 ORM 模型。"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class MediaFile(Base):
    __tablename__ = "media_files"
    __table_args__ = (
        CheckConstraint(
            "(schedule_id IS NOT NULL) OR (recipe_id IS NOT NULL)",
            name="media_must_belong_to_parent",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(), primary_key=True, default=uuid.uuid4
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(), ForeignKey("users.id"), nullable=False, index=True
    )
    schedule_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(), ForeignKey("schedules.id"), nullable=True
    )
    recipe_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(), ForeignKey("recipes.id"), nullable=True
    )
    file_type: Mapped[str] = mapped_column(String(10), nullable=False)
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )

    schedule: Mapped["Schedule | None"] = relationship("Schedule", back_populates="media_files")
    recipe: Mapped["Recipe | None"] = relationship("Recipe", back_populates="media_files")
