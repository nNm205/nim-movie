from app.database.base import Base 
from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column, relationship 
from sqlalchemy import (
    Integer,
    DateTime,
    Boolean,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint 
)

class Watchlist(Base):
    __tablename__ = "watchlist"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "movie_id",
            name="uq_user_movie_watchlist"
        ),

        CheckConstraint(
            "progress >= 0 AND progress <= 100",
            name="check_progress_range"
        )
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True, 
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

    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    progress: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    last_watched: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    is_completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    user = relationship(
        "User",
        back_populates="watchlists"
    )