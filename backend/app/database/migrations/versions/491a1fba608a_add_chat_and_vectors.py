"""add_chat_and_vectors

Revision ID: 491a1fba608a
Revises: 71e9b7e48873
Create Date: 2026-06-03 10:21:06.936028

Tạo schema cho AI Chatbot RAG (Requirements 2.1, 2.2, 3.1):
- chat_sessions: phiên hội thoại của user.
- chat_messages: message trong phiên (CHECK role ∈ {user, assistant, system}).
- movie_embeddings: vector store cho RAG retrieval với pgvector
  (CHECK source_type ∈ {movie, review}, UNIQUE (source_type, source_id, chunk_index),
  index ivfflat trên cột embedding với vector_cosine_ops).

Extensions cần thiết:
- pgvector (cột VECTOR, toán tử <=>).
- pgcrypto (gen_random_uuid() cho default chat_sessions.id).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID

from pgvector.sqlalchemy import Vector

from app.config import settings


# revision identifiers, used by Alembic.
revision: str = '491a1fba608a'
down_revision: Union[str, Sequence[str], None] = '71e9b7e48873'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ---------------------------------------------------------------
    # Extensions
    # ---------------------------------------------------------------
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    # ---------------------------------------------------------------
    # chat_sessions
    # ---------------------------------------------------------------
    op.create_table(
        "chat_sessions",
        sa.Column(
            "id",
            PG_UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=120), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
    )
    # Composite index (user_id, updated_at DESC) cho list session
    # sắp xếp theo updated_at giảm dần (Requirement 1.5).
    op.execute(
        "CREATE INDEX ix_chat_sessions_user_updated "
        "ON chat_sessions (user_id, updated_at DESC)"
    )

    # ---------------------------------------------------------------
    # chat_messages
    # ---------------------------------------------------------------
    op.create_table(
        "chat_messages",
        sa.Column(
            "id",
            sa.BigInteger(),
            primary_key=True,
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "session_id",
            PG_UUID(as_uuid=True),
            sa.ForeignKey("chat_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("role", sa.String(length=16), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("citations", JSONB(), nullable=True),
        sa.Column("tokens_input", sa.Integer(), nullable=True),
        sa.Column("tokens_output", sa.Integer(), nullable=True),
        sa.Column("metadata", JSONB(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "role IN ('user', 'assistant', 'system')",
            name="check_chat_message_role",
        ),
    )
    op.create_index(
        "ix_chat_messages_session_created",
        "chat_messages",
        ["session_id", "created_at"],
    )

    # ---------------------------------------------------------------
    # movie_embeddings
    # ---------------------------------------------------------------
    # Dimension được cố định tại migration time theo EMBEDDING_PROVIDER:
    # - local  -> all-MiniLM-L6-v2 (384)
    # - openai -> text-embedding-3-small (1536)
    # Đổi provider yêu cầu re-migrate.
    embedding_dim = settings.EMBEDDING_DIMENSION

    op.create_table(
        "movie_embeddings",
        sa.Column(
            "id",
            sa.BigInteger(),
            primary_key=True,
            autoincrement=True,
            nullable=False,
        ),
        sa.Column("source_type", sa.String(length=16), nullable=False),
        sa.Column("source_id", sa.BigInteger(), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(embedding_dim), nullable=False),
        sa.Column("metadata", JSONB(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "source_type IN ('movie', 'review')",
            name="check_movie_embedding_source_type",
        ),
        sa.UniqueConstraint(
            "source_type",
            "source_id",
            "chunk_index",
            name="uq_movie_embeddings_chunk",
        ),
    )
    # Index cho cache invalidation và delete by source (Requirement 6.5).
    op.create_index(
        "ix_movie_embeddings_source",
        "movie_embeddings",
        ["source_type", "source_id"],
    )
    # ANN index cho cosine similarity search trên pgvector (Requirements 3.1, 14.2).
    op.execute(
        "CREATE INDEX ix_movie_embeddings_embedding "
        "ON movie_embeddings USING ivfflat (embedding vector_cosine_ops) "
        "WITH (lists = 100)"
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop theo thứ tự ngược của upgrade.

    # movie_embeddings
    op.execute("DROP INDEX IF EXISTS ix_movie_embeddings_embedding")
    op.drop_index("ix_movie_embeddings_source", table_name="movie_embeddings")
    op.drop_table("movie_embeddings")

    # chat_messages
    op.drop_index("ix_chat_messages_session_created", table_name="chat_messages")
    op.drop_table("chat_messages")

    # chat_sessions
    op.execute("DROP INDEX IF EXISTS ix_chat_sessions_user_updated")
    op.drop_table("chat_sessions")

    # Không drop extension vector / pgcrypto: có thể được dùng bởi
    # schema khác, để admin xử lý thủ công nếu cần.
