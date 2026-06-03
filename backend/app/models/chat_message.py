import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class ChatSession(Base):
    """
    Một phiên hội thoại của một user (Conversation).

    Schema theo design "Data Models" - Requirement 2.1:
    - id: UUID v4 PK (default tạo ở Python để consistent với non-pgcrypto env).
    - user_id: FK -> users.id, ON DELETE CASCADE.
    - title: 60 ký tự đầu của message đầu tiên (nullable cho session vừa tạo).
    - created_at / updated_at: timestamptz, được Chat_Service touch khi append message.
    """

    __tablename__ = "chat_sessions"

    __table_args__ = (
        Index(
            "ix_chat_sessions_user_updated",
            "user_id",
            "updated_at",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    title: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    messages = relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at",
    )


class ChatMessage(Base):
    """
    Một message trong ChatSession.

    Schema theo design "Data Models" - Requirement 2.2:
    - role ∈ {"user","assistant","system"} (CHECK constraint).
    - citations JSONB cho assistant message: [{source_type, source_id}, ...].
    - metadata JSONB cho `{partial: bool, error: str?}` (Requirements 5.4, 9.7).
      Tên Python attribute là `metadata_` vì `metadata` bị Base reserve;
      cột DB vẫn tên `metadata`.
    """

    __tablename__ = "chat_messages"

    __table_args__ = (
        CheckConstraint(
            "role IN ('user', 'assistant', 'system')",
            name="check_chat_message_role",
        ),
        Index(
            "ix_chat_messages_session_created",
            "session_id",
            "created_at",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    session_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    citations: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    tokens_input: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    tokens_output: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    # `metadata` là attribute dành riêng cho Base.metadata; ta map Python attr
    # `metadata_` sang cột DB tên "metadata".
    metadata_: Mapped[dict | None] = mapped_column(
        "metadata",
        JSONB,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    session = relationship(
        "ChatSession",
        back_populates="messages",
    )
