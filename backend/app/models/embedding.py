from datetime import datetime, timezone

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.config import settings
from app.database.base import Base


class MovieEmbedding(Base):
    """
    Một Document_Chunk được index cho RAG retrieval (Requirement 3.1).

    Mapping schema:
    - id: BIGSERIAL PK.
    - source_type ∈ {"movie","review"} (CHECK).
    - source_id: TMDB movie id hoặc review id.
    - chunk_index: 0 = summary, ≥1 = cast/review chunk.
    - embedding: Vector(EMBEDDING_DIMENSION) — cố định tại migration.
    - metadata JSONB: {movie_id, year, genres[], rating?, review_id?}.
      Tên Python attribute là `metadata_` (ánh xạ qua cột DB `metadata`)
      do `Base.metadata` reserved.

    Constraints:
    - UNIQUE (source_type, source_id, chunk_index) tên uq_movie_embeddings_chunk
      hỗ trợ idempotent upsert (Requirement 3.6).
    """

    __tablename__ = "movie_embeddings"

    __table_args__ = (
        CheckConstraint(
            "source_type IN ('movie', 'review')",
            name="check_movie_embedding_source_type",
        ),
        UniqueConstraint(
            "source_type",
            "source_id",
            "chunk_index",
            name="uq_movie_embeddings_chunk",
        ),
        Index(
            "ix_movie_embeddings_source",
            "source_type",
            "source_id",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    source_type: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
    )

    source_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    embedding: Mapped[list[float]] = mapped_column(
        Vector(settings.EMBEDDING_DIMENSION),
        nullable=False,
    )

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
