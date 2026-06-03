"""Vector_Store cho AI Chatbot RAG.

Lớp truy cập dữ liệu cho bảng ``movie_embeddings`` (xem
``app/models/embedding.py``) với pgvector trên Supabase Postgres. Module
chỉ chứa data-access primitives, không có logic RAG (ranking, cache,
personalization). Phía trên là :class:`app.services.ai.rag_service.RAGService`.

Tham chiếu Requirements:

* 3.1 — vector schema cho movie + review chunks; ANN search theo cosine
  distance.
* 3.6, 3.7 — idempotent upsert: cùng input không tạo row mới, chỉ thay đổi
  content mới gây UPDATE.
* 4.2 — top-K similarity retrieval, sort theo score giảm dần.

Design notes (xem ``design.md`` mục Vector_Store):

* ``similarity_search`` dùng raw SQL qua :func:`sqlalchemy.text` với toán tử
  ``<=>`` (cosine distance) của pgvector và quy về similarity bằng ``1 - dist``.
  Bind ``:q`` qua :class:`pgvector.sqlalchemy.Vector` để adapter tự cast list
  Python sang ``vector(N)``.
* ``upsert_chunk`` dùng ``INSERT ... ON CONFLICT ... DO UPDATE ... WHERE
  movie_embeddings.content IS DISTINCT FROM EXCLUDED.content RETURNING ...``.
  Mẹo phân biệt insert/update: cột hệ thống ``xmax`` của RETURNING bằng 0 với
  dòng mới insert, khác 0 với dòng vừa được UPDATE bởi mệnh đề ON CONFLICT.
  Khi WHERE chặn UPDATE (content không đổi), RETURNING không trả row → skip.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Final, Literal, Sequence

from pgvector.sqlalchemy import Vector
from sqlalchemy import Integer, bindparam, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Session

from app.config import settings

__all__ = [
    "RetrievedChunk",
    "UpsertResult",
    "VectorStore",
]


SourceType = Literal["movie", "review"]


# Tập source_type hợp lệ — khớp CHECK constraint của bảng và CitationCodec.
_VALID_SOURCE_TYPES: Final[frozenset[str]] = frozenset({"movie", "review"})


@dataclass(frozen=True)
class RetrievedChunk:
    """Một chunk được trả về từ similarity search.

    Attributes:
        id: PK của row trong ``movie_embeddings``.
        source_type: ``"movie"`` hoặc ``"review"``.
        source_id: TMDB movie id hoặc review id (kiểu ``BIGINT`` ở DB, fit ``int``).
        chunk_index: 0 = summary movie / chunk đầu review; ≥1 = cast/director
            hoặc chunk tiếp theo của review.
        content: Nội dung text của chunk.
        score: Similarity score, ``1 - cosine_distance``. Càng gần 1 càng tương
            tự với truy vấn; theo design có thể âm nếu vector ngược hướng.
        metadata: Metadata JSONB (``{movie_id, year, genres, rating?, review_id?}``).
            Trả về ``{}`` khi cột DB là NULL để consumer không phải null-check.
    """

    id: int
    source_type: SourceType
    source_id: int
    chunk_index: int
    content: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class UpsertResult:
    """Kết quả của một :meth:`VectorStore.upsert_chunk`.

    ``action`` cho biết hành động đã thực hiện:

    * ``"inserted"``: dòng mới được thêm.
    * ``"updated"``: dòng cũ tồn tại nhưng ``content`` khác → đã UPDATE.
    * ``"skipped"``: dòng cũ tồn tại và content không đổi (Requirement 3.6).
    """

    action: Literal["inserted", "updated", "skipped"]


# ---------------------------------------------------------------------------
# SQL statements
# ---------------------------------------------------------------------------

# similarity_search: dùng <=> (cosine distance), score = 1 - distance.
# WHERE clause dynamic theo có filter_source_types không.
_SQL_SIMILARITY = """
SELECT id, source_type, source_id, chunk_index, content, metadata,
       1 - (embedding <=> :q) AS score
FROM movie_embeddings
{where_clause}
ORDER BY embedding <=> :q
LIMIT :k
"""

# upsert_chunk:
#   - ON CONFLICT (source_type, source_id, chunk_index) trùng với
#     uq_movie_embeddings_chunk (Requirement 3.6).
#   - WHERE movie_embeddings.content IS DISTINCT FROM EXCLUDED.content giữ
#     idempotency: input không đổi → UPDATE bị bỏ qua → RETURNING rỗng → skip.
#   - (xmax = 0) AS inserted: khi tuple mới được insert (không conflict), xmax
#     của tuple đó = 0; với UPDATE qua ON CONFLICT, xmax sẽ khác 0.
_SQL_UPSERT = """
INSERT INTO movie_embeddings
    (source_type, source_id, chunk_index, content, embedding, metadata)
VALUES
    (:source_type, :source_id, :chunk_index, :content, :embedding, :metadata)
ON CONFLICT (source_type, source_id, chunk_index)
DO UPDATE SET
    content = EXCLUDED.content,
    embedding = EXCLUDED.embedding,
    metadata = EXCLUDED.metadata
WHERE movie_embeddings.content IS DISTINCT FROM EXCLUDED.content
RETURNING id, (xmax = 0) AS inserted
"""

_SQL_DELETE_BY_SOURCE = """
DELETE FROM movie_embeddings
WHERE source_type = :source_type AND source_id = :source_id
"""

_SQL_COUNT = "SELECT COUNT(*) FROM movie_embeddings"


def _coerce_metadata(raw: Any) -> dict[str, Any]:
    """Chuẩn hoá metadata trả về thành ``dict``.

    Postgres JSONB qua psycopg2/pgvector adapter thường trả ``dict`` sẵn, nhưng
    có driver/path trả ``str`` JSON hoặc ``None`` — chúng ta normalize về
    ``dict`` để consumer dùng nhất quán.
    """
    if raw is None:
        return {}
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            decoded = json.loads(raw)
        except json.JSONDecodeError:
            return {}
        return decoded if isinstance(decoded, dict) else {}
    # Lạ — best-effort, không raise để khỏi gãy retrieval.
    return {}


class VectorStore:
    """Data-access layer cho bảng ``movie_embeddings``.

    Sử dụng synchronous :class:`sqlalchemy.orm.Session` khớp pattern hiện tại
    của :mod:`app.database.session`. Không tự mở/commit transaction — caller
    quản lý lifecycle (Indexing_Job hoặc test fixture sẽ gọi ``session.commit()``
    sau khi upsert).

    Args:
        db: Một :class:`Session` đã được mở. Lifecycle do caller quản.
        dimension: Số chiều của vector trong bảng. Mặc định lấy từ
            ``settings.EMBEDDING_DIMENSION``; cho phép override để dễ test
            (vd unit test với dim=3) hoặc trong môi trường có nhiều provider.

    Note:
        Đổi ``EMBEDDING_PROVIDER`` đòi hỏi re-migrate vì cột ``embedding`` được
        khai báo ``vector(N)`` cố định tại migration (xem design.md).
    """

    def __init__(self, db: Session, *, dimension: int | None = None) -> None:
        self._db = db
        self._dimension = (
            int(dimension) if dimension is not None else int(settings.EMBEDDING_DIMENSION)
        )

    # ------------------------------------------------------------------
    # Read paths
    # ------------------------------------------------------------------

    def similarity_search(
        self,
        embedding: Sequence[float],
        top_k: int = 8,
        filter_source_types: Sequence[str] | None = None,
    ) -> list[RetrievedChunk]:
        """ANN top-K theo cosine similarity (Requirements 3.1, 4.2).

        Args:
            embedding: Vector truy vấn dạng list/tuple float, độ dài phải khớp
                ``dimension`` của bảng (pgvector sẽ raise nếu lệch).
            top_k: Số chunk trả về tối đa. Mặc định 8 (Requirement 4.2).
            filter_source_types: Hạn chế kết quả theo ``source_type``. ``None``
                hoặc danh sách rỗng → không filter. Mỗi phần tử phải thuộc
                ``{"movie", "review"}``; phần tử không hợp lệ bị raise sớm để
                fail fast.

        Returns:
            Danh sách :class:`RetrievedChunk` đã sắp theo score giảm dần
            (tương đương distance tăng dần). ``[]`` nếu bảng rỗng hoặc filter
            không match row nào.

        Raises:
            ValueError: ``top_k <= 0``, ``embedding`` rỗng, hoặc
                ``filter_source_types`` chứa giá trị không hợp lệ.
        """
        if top_k <= 0:
            raise ValueError(f"top_k must be > 0, got {top_k}")
        if not embedding:
            raise ValueError("embedding must be a non-empty sequence of floats")

        params: dict[str, Any] = {
            "q": list(embedding),
            "k": int(top_k),
        }
        binds = [
            bindparam("q", type_=Vector(self._dimension)),
            bindparam("k", type_=Integer()),
        ]

        if filter_source_types:
            normalized = [str(s) for s in filter_source_types]
            invalid = [s for s in normalized if s not in _VALID_SOURCE_TYPES]
            if invalid:
                raise ValueError(
                    f"filter_source_types chứa giá trị không hợp lệ: {invalid!r}; "
                    f"chỉ chấp nhận {sorted(_VALID_SOURCE_TYPES)!r}"
                )
            where_clause = "WHERE source_type IN :types"
            binds.append(bindparam("types", expanding=True))
            params["types"] = normalized
        else:
            where_clause = ""

        stmt = text(_SQL_SIMILARITY.format(where_clause=where_clause)).bindparams(*binds)

        rows = self._db.execute(stmt, params).all()
        results: list[RetrievedChunk] = []
        for row in rows:
            # row có thể là Row (named tuple) — truy cập theo tên cho an toàn.
            results.append(
                RetrievedChunk(
                    id=int(row.id),
                    source_type=row.source_type,  # type: ignore[arg-type]
                    source_id=int(row.source_id),
                    chunk_index=int(row.chunk_index),
                    content=row.content,
                    score=float(row.score),
                    metadata=_coerce_metadata(row.metadata),
                )
            )
        return results

    def count(self) -> int:
        """Tổng số row trong bảng ``movie_embeddings``."""
        result = self._db.execute(text(_SQL_COUNT)).scalar()
        return int(result or 0)

    # ------------------------------------------------------------------
    # Write paths
    # ------------------------------------------------------------------

    def upsert_chunk(
        self,
        source_type: str,
        source_id: int,
        chunk_index: int,
        content: str,
        embedding: Sequence[float],
        metadata: dict[str, Any] | None = None,
    ) -> UpsertResult:
        """Idempotent upsert một chunk (Requirements 3.6, 3.7).

        Hành vi:

        * Row chưa tồn tại với khoá ``(source_type, source_id, chunk_index)``
          → INSERT mới, trả ``UpsertResult("inserted")``.
        * Row đã tồn tại và ``content`` khác giá trị mới → UPDATE
          ``content``, ``embedding``, ``metadata``, trả ``UpsertResult("updated")``.
        * Row đã tồn tại và ``content`` không đổi → bỏ qua (Requirement 3.6),
          trả ``UpsertResult("skipped")``. Lưu ý: chỉ so sánh ``content``;
          embedding/metadata thay đổi mà content giống nhau thì coi như
          ``skipped`` để giữ deterministic behavior cho re-index batch.

        Args:
            source_type: ``"movie"`` hoặc ``"review"``.
            source_id: ID nguồn (>0).
            chunk_index: Thứ tự chunk (≥0).
            content: Nội dung text non-empty.
            embedding: Vector ``[float; dimension]``.
            metadata: Metadata JSONB; ``None`` được lưu thành SQL ``NULL``.

        Returns:
            :class:`UpsertResult` với action tương ứng.

        Raises:
            ValueError: Tham số không hợp lệ (source_type lạ, id ≤ 0,
                chunk_index < 0, content rỗng, embedding rỗng).
        """
        if source_type not in _VALID_SOURCE_TYPES:
            raise ValueError(
                f"source_type phải thuộc {sorted(_VALID_SOURCE_TYPES)!r}, "
                f"nhận {source_type!r}"
            )
        if not isinstance(source_id, int) or isinstance(source_id, bool) or source_id <= 0:
            raise ValueError(f"source_id phải là int > 0, nhận {source_id!r}")
        if not isinstance(chunk_index, int) or isinstance(chunk_index, bool) or chunk_index < 0:
            raise ValueError(f"chunk_index phải là int >= 0, nhận {chunk_index!r}")
        if not content:
            raise ValueError("content không được rỗng")
        if not embedding:
            raise ValueError("embedding phải là sequence float non-empty")

        stmt = text(_SQL_UPSERT).bindparams(
            bindparam("source_type"),
            bindparam("source_id", type_=Integer()),
            bindparam("chunk_index", type_=Integer()),
            bindparam("content"),
            bindparam("embedding", type_=Vector(self._dimension)),
            bindparam("metadata", type_=JSONB()),
        )
        params: dict[str, Any] = {
            "source_type": source_type,
            "source_id": int(source_id),
            "chunk_index": int(chunk_index),
            "content": content,
            "embedding": list(embedding),
            "metadata": metadata,
        }

        row = self._db.execute(stmt, params).first()
        if row is None:
            # WHERE clause chặn UPDATE → không có row trả về.
            return UpsertResult(action="skipped")
        # row.inserted: True nếu INSERT mới, False nếu UPDATE.
        if bool(row.inserted):
            return UpsertResult(action="inserted")
        return UpsertResult(action="updated")

    def delete_by_source(self, source_type: str, source_id: int) -> int:
        """Xoá toàn bộ chunk theo ``(source_type, source_id)``.

        Dùng khi review bị xoá hoặc admin force re-index sạch một movie
        (Requirement 3.7 — lifecycle delete).

        Args:
            source_type: ``"movie"`` hoặc ``"review"``.
            source_id: ID nguồn (>0).

        Returns:
            Số row đã xoá.

        Raises:
            ValueError: Tham số không hợp lệ.
        """
        if source_type not in _VALID_SOURCE_TYPES:
            raise ValueError(
                f"source_type phải thuộc {sorted(_VALID_SOURCE_TYPES)!r}, "
                f"nhận {source_type!r}"
            )
        if not isinstance(source_id, int) or isinstance(source_id, bool) or source_id <= 0:
            raise ValueError(f"source_id phải là int > 0, nhận {source_id!r}")

        stmt = text(_SQL_DELETE_BY_SOURCE).bindparams(
            bindparam("source_type"),
            bindparam("source_id", type_=Integer()),
        )
        result = self._db.execute(
            stmt,
            {"source_type": source_type, "source_id": int(source_id)},
        )
        # rowcount có thể là -1 trên một số driver nếu không xác định được;
        # với psycopg2 + DELETE thường trả số chính xác. Bảo vệ tối thiểu.
        rowcount = result.rowcount
        return int(rowcount) if rowcount is not None and rowcount >= 0 else 0
