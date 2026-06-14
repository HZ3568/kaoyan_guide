from datetime import datetime
from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class LearningProfile(Base):
    __tablename__ = "learning_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    target_school: Mapped[str | None] = mapped_column(String(128))
    target_major: Mapped[str | None] = mapped_column(String(128))
    target_score: Mapped[int | None] = mapped_column(Integer)
    exam_date: Mapped[str | None] = mapped_column(String(32))
    current_level: Mapped[str | None] = mapped_column(String(64))
    weak_subjects: Mapped[list | None] = mapped_column(JSON)
    daily_available_hours: Mapped[float] = mapped_column(Float, default=3.0)
    weekly_available_days: Mapped[int] = mapped_column(Integer, default=6)
    learning_preference: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
