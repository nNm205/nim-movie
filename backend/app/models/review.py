from datetime import datetime, timezone
from sqlalchemy import (
    Integer,
    Text,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

class Review(Base):
    __tablename__ = "reviews"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "movie_id",
            name="uq_user_movie_review"
        ),

        CheckConstraint(
            "rating >= 1 AND rating <= 10",
            name="check_rating_range"
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    movie_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    rating: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    review_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    user = relationship(
        "User",
        back_populates="reviews"
    )