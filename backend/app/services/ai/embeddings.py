"""Embedding_Service + Document_Chunker cho AI Chatbot RAG.

Module này gồm hai phần:

1. **Document_Chunker** (`chunk_text`, `chunk_movie`, `chunk_review`) phục vụ
   Indexing_Job — đã wire ở task 6.1.
2. **Embedding_Service** (`EmbeddingService`, `LocalSentenceTransformerEmbedder`,
   `OpenAIEmbedder`, `build_embedding_service`) — wire ở task 6.4.

Tham chiếu Requirements:

* 3.2, 3.3 — cấu hình hai backend (`local` / `openai`) qua env, dimension cố định
  384 (MiniLM) hoặc 1536 (`text-embedding-3-small`).
* 3.4 — chunk movie: chunk 0 là summary ``"{title} ({year}) - {genres}. {overview}"``,
  các chunk tiếp theo cho top-10 cast + 1 director.
* 3.5 — chunk review: chỉ index khi ``review_text`` non-null, chia theo
  ``chunk_text`` (max 512 token, overlap 50), metadata
  ``{movie_id, rating, review_id}``.
* 4.1 — mọi user message phải đi qua ``EmbeddingService.embed`` trước khi RAG
  retrieve.
* 6.1, 6.2 — cache key ``embed:{provider}:{sha256(text)}``, TTL 3600s.

Token boundary dùng ``tiktoken.get_encoding("cl100k_base")`` (xem design.md
mục Embedding_Service và bảng quyết định kỹ thuật về tokenizer).
"""

from __future__ import annotations

import asyncio
import hashlib
import threading
from typing import Any, Iterable, Mapping, Protocol, TypedDict, runtime_checkable

import httpx
import tiktoken
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.integrations.cache_manager import CacheManager

__all__ = [
    "ChunkInput",
    "chunk_text",
    "chunk_movie",
    "chunk_review",
    "EmbeddingBackend",
    "LocalSentenceTransformerEmbedder",
    "OpenAIEmbedder",
    "EmbeddingService",
    "build_embedding_service",
]


class ChunkInput(TypedDict):
    """Một Document_Chunk chuẩn bị để upsert vào Vector_Store.

    Attributes:
        chunk_index: Thứ tự chunk trong cùng nguồn (0-based).
        content: Nội dung text của chunk.
        metadata: Metadata kèm theo (movie_id, year, genres, source, ...).
    """

    chunk_index: int
    content: str
    metadata: dict[str, Any]


# ---------------------------------------------------------------------------
# tiktoken encoding cache
# ---------------------------------------------------------------------------

# Khởi tạo encoder lười để không trả phí ở import time, nhưng cache lại để
# các lời gọi sau (đặc biệt trong Indexing_Job) không phải reload bảng BPE.
_ENCODER: tiktoken.Encoding | None = None


def _get_encoder() -> tiktoken.Encoding:
    global _ENCODER
    if _ENCODER is None:
        _ENCODER = tiktoken.get_encoding("cl100k_base")
    return _ENCODER


# ---------------------------------------------------------------------------
# chunk_text
# ---------------------------------------------------------------------------


def chunk_text(
    text: str,
    max_tokens: int = 512,
    overlap_tokens: int = 50,
) -> list[str]:
    """Cắt ``text`` thành danh sách chunk ở token boundary.

    Sliding window với cửa sổ ``max_tokens`` token và stride
    ``max_tokens - overlap_tokens``; hai chunk liên tiếp share đúng
    ``overlap_tokens`` token (Requirement 3.5).

    Args:
        text: Nội dung text gốc. ``""`` hoặc ``None``-equivalent (chuỗi
            chỉ chứa whitespace là OK — chỉ rỗng theo nghĩa
            ``len(tokens) == 0`` mới trả ``[]``).
        max_tokens: Số token tối đa mỗi chunk. Mặc định 512.
        overlap_tokens: Số token chồng giữa hai chunk liên tiếp. Mặc định 50.

    Returns:
        Danh sách chuỗi đã decode. ``[]`` nếu ``text`` không có token nào.
        Một phần tử duy nhất ``[text]`` nếu toàn bộ text fit trong một chunk.

    Raises:
        ValueError: Khi ``max_tokens <= 0`` hoặc ``overlap_tokens < 0`` hoặc
            ``overlap_tokens >= max_tokens`` (sẽ gây vòng lặp vô hạn).
    """
    if max_tokens <= 0:
        raise ValueError(f"max_tokens must be > 0, got {max_tokens}")
    if overlap_tokens < 0:
        raise ValueError(f"overlap_tokens must be >= 0, got {overlap_tokens}")
    if overlap_tokens >= max_tokens:
        raise ValueError(
            f"overlap_tokens ({overlap_tokens}) must be < max_tokens "
            f"({max_tokens})"
        )

    if not text:
        return []

    encoder = _get_encoder()
    tokens = encoder.encode(text)
    if not tokens:
        return []

    if len(tokens) <= max_tokens:
        # Trả nguyên text gốc để giữ whitespace / boundary chính xác.
        return [text]

    stride = max_tokens - overlap_tokens
    chunks: list[str] = []
    start = 0
    n = len(tokens)
    while start < n:
        end = start + max_tokens
        window = tokens[start:end]
        chunks.append(encoder.decode(window))
        if end >= n:
            break
        start += stride
    return chunks


# ---------------------------------------------------------------------------
# duck-typed accessor
# ---------------------------------------------------------------------------


def _get(obj: Any, key: str, default: Any = None) -> Any:
    """Truy cập field theo cả Mapping (dict) lẫn object có attribute.

    TMDb client hiện trả về ``dict`` thô (xem ``app/integrations/tmdb_client.py``)
    nhưng task 6.4 có thể gói lại thành dataclass — accessor này hoạt động cho
    cả hai mà không phải sửa chunker.
    """
    if obj is None:
        return default
    if isinstance(obj, Mapping):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _extract_year(release_date: Any) -> str:
    """Lấy phần năm từ release_date dạng ``YYYY-MM-DD`` hoặc object có
    ``.year``. Trả về chuỗi rỗng khi không xác định được."""
    if release_date is None or release_date == "":
        return ""
    # date / datetime
    year_attr = getattr(release_date, "year", None)
    if isinstance(year_attr, int):
        return str(year_attr)
    # string "YYYY-MM-DD"
    if isinstance(release_date, str):
        return release_date[:4] if len(release_date) >= 4 else ""
    return ""


def _genres_to_names(genres: Any) -> list[str]:
    """Chuẩn hoá field ``genres`` thành list[str] tên thể loại.

    Hỗ trợ:
    - ``[{"id": 28, "name": "Action"}, ...]`` (TMDb detail).
    - ``["Action", "Drama"]`` (đã pre-process).
    - ``None`` → ``[]``.
    """
    if not genres:
        return []
    names: list[str] = []
    for g in genres:
        if isinstance(g, str):
            if g:
                names.append(g)
        else:
            name = _get(g, "name")
            if isinstance(name, str) and name:
                names.append(name)
    return names


def _find_director(crew: Iterable[Any] | None) -> Any | None:
    """Trả về phần tử crew đầu tiên có ``job == "Director"``."""
    if not crew:
        return None
    for member in crew:
        job = _get(member, "job")
        if isinstance(job, str) and job.lower() == "director":
            return member
    return None


# ---------------------------------------------------------------------------
# chunk_movie
# ---------------------------------------------------------------------------


def chunk_movie(movie: Any) -> list[ChunkInput]:
    """Sinh danh sách ``ChunkInput`` cho một movie từ TMDB.

    Theo Requirement 3.4:

    * Chunk 0 — ``summary``: ``"{title} ({year}) - {genres_csv}. {overview}"``.
    * Chunk 1..K (K ≤ 10) — top-10 cast: mỗi diễn viên một chunk.
    * Chunk K+1 (nếu có director) — director.

    Args:
        movie: Payload movie. Hỗ trợ ``Mapping`` (dict TMDb thô) hoặc object
            có attribute. Các field được đọc: ``id``, ``title``,
            ``release_date`` (hoặc ``year``), ``genres``, ``overview``,
            ``cast``, ``crew``. Nếu credits nằm trong key ``credits``
            (TMDb ``movie/{id}?append_to_response=credits``), accessor sẽ
            unwrap nó.

    Returns:
        Danh sách :class:`ChunkInput` với ``chunk_index`` tăng dần từ 0.
    """
    movie_id = _get(movie, "id")
    title = _get(movie, "title") or _get(movie, "name") or ""
    overview = _get(movie, "overview") or ""

    year_field = _get(movie, "year")
    if year_field is None or year_field == "":
        year = _extract_year(_get(movie, "release_date"))
    else:
        year = str(year_field)

    genre_names = _genres_to_names(_get(movie, "genres"))
    genres_csv = ", ".join(genre_names)

    # TMDb có thể nest credits trong key "credits"
    credits = _get(movie, "credits")
    cast = _get(movie, "cast")
    crew = _get(movie, "crew")
    if cast is None and credits is not None:
        cast = _get(credits, "cast")
    if crew is None and credits is not None:
        crew = _get(credits, "crew")

    base_metadata: dict[str, Any] = {
        "movie_id": movie_id,
        "year": year or None,
        "genres": genre_names,
        "source": "movie",
    }

    chunks: list[ChunkInput] = []

    # Chunk 0 — summary (Requirement 3.4).
    summary = f"{title} ({year}) - {genres_csv}. {overview}"
    chunks.append(
        ChunkInput(
            chunk_index=0,
            content=summary,
            metadata={**base_metadata, "kind": "summary"},
        )
    )

    next_index = 1

    # Top-10 cast.
    if cast:
        for member in list(cast)[:10]:
            name = _get(member, "name") or ""
            character = _get(member, "character") or ""
            if not name:
                continue
            if character:
                content = f"{name} đóng vai {character} trong {title} ({year})."
            else:
                content = f"{name} đóng trong {title} ({year})."
            chunks.append(
                ChunkInput(
                    chunk_index=next_index,
                    content=content,
                    metadata={
                        **base_metadata,
                        "kind": "cast",
                        "person_id": _get(member, "id"),
                        "person_name": name,
                        "character": character or None,
                    },
                )
            )
            next_index += 1

    # 1 director.
    director = _find_director(crew)
    if director is not None:
        director_name = _get(director, "name") or ""
        if director_name:
            chunks.append(
                ChunkInput(
                    chunk_index=next_index,
                    content=f"{director_name} đạo diễn {title} ({year}).",
                    metadata={
                        **base_metadata,
                        "kind": "director",
                        "person_id": _get(director, "id"),
                        "person_name": director_name,
                    },
                )
            )
            next_index += 1

    return chunks


# ---------------------------------------------------------------------------
# chunk_review
# ---------------------------------------------------------------------------


def chunk_review(review: Any) -> list[ChunkInput]:
    """Sinh ``ChunkInput`` cho một review.

    Theo Requirement 3.5: chỉ index khi ``review_text`` non-null/non-empty;
    chia text bằng :func:`chunk_text` (mặc định max 512 token, overlap 50);
    metadata ``{movie_id, rating, review_id, source: "review"}``.

    Args:
        review: Đối tượng review (SQLAlchemy ``Review`` hoặc dict). Cần các
            field ``id``, ``movie_id``, ``rating``, ``review_text``.

    Returns:
        ``[]`` khi không có ``review_text``; ngược lại danh sách chunk theo
        thứ tự xuất hiện.
    """
    review_text = _get(review, "review_text")
    if not review_text or not str(review_text).strip():
        return []

    movie_id = _get(review, "movie_id")
    rating = _get(review, "rating")
    review_id = _get(review, "id")

    pieces = chunk_text(review_text)
    base_metadata: dict[str, Any] = {
        "movie_id": movie_id,
        "rating": rating,
        "review_id": review_id,
        "source": "review",
    }

    return [
        ChunkInput(
            chunk_index=i,
            content=piece,
            metadata=dict(base_metadata),
        )
        for i, piece in enumerate(pieces)
    ]


# ---------------------------------------------------------------------------
# EmbeddingBackend Protocol
# ---------------------------------------------------------------------------


@runtime_checkable
class EmbeddingBackend(Protocol):
    """Backend nhỏ tách rời khỏi cache layer.

    Lý do tách: ``EmbeddingService`` chịu trách nhiệm cache + key convention
    (Requirement 6.1, 6.2); backend chỉ lo gọi model. Điều này giúp:

    * Test cache layer bằng fake backend đếm số lần encode.
    * Swap backend (local / openai / mock) không phải sửa cache.
    """

    @property
    def dimension(self) -> int:
        """Số chiều của vector trả về (cố định cho mỗi backend)."""
        ...

    async def embed_one(self, text: str) -> list[float]:
        """Encode một đoạn text → vector ``[float; dimension]``."""
        ...

    async def embed_many(self, texts: list[str]) -> list[list[float]]:
        """Batch encode — dùng cho Indexing_Job."""
        ...


# ---------------------------------------------------------------------------
# LocalSentenceTransformerEmbedder
# ---------------------------------------------------------------------------


class LocalSentenceTransformerEmbedder:
    """Backend dùng ``sentence-transformers/all-MiniLM-L6-v2`` (384d).

    Model được lazy-load lần đầu gọi và cache ở **class level** để mọi
    instance trong process share cùng một model — tránh tốn vài trăm MB cho
    mỗi service. Khoá ``threading.Lock`` chống race khi nhiều worker async
    cùng lúc trigger first-call.

    ``model.encode`` là CPU-bound và blocking; ta gọi qua
    :func:`asyncio.to_thread` để không block event loop của FastAPI
    (Requirement 4.1 — mọi user message đi qua embed, không được làm chậm
    pipeline streaming).
    """

    DEFAULT_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    DEFAULT_DIMENSION: int = 384

    # Class-level singleton cache: {model_name: model_instance}.
    _model_cache: dict[str, Any] = {}
    _model_lock: threading.Lock = threading.Lock()

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL_NAME,
        dimension: int = DEFAULT_DIMENSION,
    ) -> None:
        self._model_name = model_name
        self._dimension = dimension

    @property
    def dimension(self) -> int:
        return self._dimension

    def _load_model(self) -> Any:
        """Lazy-load model, share giữa các instance cùng ``model_name``.

        Import ``sentence_transformers`` muộn để module này import được kể cả
        khi gói chưa được cài (ví dụ chạy unit test cho chunker mà không
        muốn pull weights). ``RuntimeError`` rõ ràng để callers biết phải cài
        thêm.
        """
        cached = self._model_cache.get(self._model_name)
        if cached is not None:
            return cached
        with self._model_lock:
            cached = self._model_cache.get(self._model_name)
            if cached is not None:
                return cached
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError as exc:  # pragma: no cover - phụ thuộc môi trường
                raise RuntimeError(
                    "sentence-transformers chưa được cài. Chạy "
                    "`pip install sentence-transformers>=2.7` hoặc đổi "
                    "EMBEDDING_PROVIDER=openai."
                ) from exc
            model = SentenceTransformer(self._model_name)
            self._model_cache[self._model_name] = model
            return model

    def _encode_sync(self, texts: list[str]) -> list[list[float]]:
        """Chạy ``model.encode`` đồng bộ — gọi từ threadpool worker."""
        model = self._load_model()
        # ``convert_to_numpy=True`` (default) trả ndarray; ``.tolist()``
        # để giao diện ổn định và serializable cho cache.
        embeddings = model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=False,
        )
        return [list(map(float, vec)) for vec in embeddings]

    async def embed_one(self, text: str) -> list[float]:
        result = await asyncio.to_thread(self._encode_sync, [text])
        return result[0]

    async def embed_many(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        return await asyncio.to_thread(self._encode_sync, list(texts))


# ---------------------------------------------------------------------------
# OpenAIEmbedder
# ---------------------------------------------------------------------------


class _OpenAITransientError(Exception):
    """Lỗi tạm thời (5xx, timeout, network) — đáng retry."""


def _is_retryable_http_status(exc: BaseException) -> bool:
    if isinstance(exc, httpx.HTTPStatusError):
        status = exc.response.status_code
        return status >= 500 or status == 429
    return False


class OpenAIEmbedder:
    """Backend dùng OpenAI ``text-embedding-3-small`` (1536d).

    * HTTP qua ``httpx.AsyncClient`` để tận dụng connection pooling.
    * Retry 2 lần (tổng 3 attempts) với exponential backoff 1s → 2s khi gặp
      timeout, lỗi mạng, hoặc HTTP 5xx/429 (Requirement 9.6 phong cách —
      embedding cũng cần resilient để pipeline RAG không gãy).
    """

    DEFAULT_MODEL_NAME: str = "text-embedding-3-small"
    DEFAULT_DIMENSION: int = 1536
    DEFAULT_BASE_URL: str = "https://api.openai.com/v1"
    DEFAULT_TIMEOUT_SECONDS: float = 30.0

    def __init__(
        self,
        api_key: str,
        model_name: str = DEFAULT_MODEL_NAME,
        dimension: int = DEFAULT_DIMENSION,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        if not api_key:
            raise ValueError("OpenAIEmbedder yêu cầu api_key non-empty.")
        self._api_key = api_key
        self._model_name = model_name
        self._dimension = dimension
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds
        self._client = client  # nếu None, tạo lazy theo lifecycle

    @property
    def dimension(self) -> int:
        return self._dimension

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self._timeout_seconds,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
            )
        return self._client

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    @retry(
        stop=stop_after_attempt(3),  # 1 lần đầu + 2 retry
        wait=wait_exponential(multiplier=1, min=1, max=2),
        retry=(
            retry_if_exception_type(httpx.TimeoutException)
            | retry_if_exception_type(httpx.TransportError)
            | retry_if_exception_type(_OpenAITransientError)
        ),
        reraise=True,
    )
    async def _post_embeddings(self, inputs: list[str]) -> list[list[float]]:
        client = self._get_client()
        url = f"{self._base_url}/embeddings"
        payload: dict[str, Any] = {
            "model": self._model_name,
            "input": inputs,
        }
        response = await client.post(url, json=payload)
        if response.status_code >= 500 or response.status_code == 429:
            # Convert thành lỗi retryable để tenacity bắt.
            raise _OpenAITransientError(
                f"OpenAI embeddings transient error: HTTP "
                f"{response.status_code} {response.text[:200]}"
            )
        response.raise_for_status()
        body = response.json()
        data = body.get("data") or []
        # OpenAI trả về list theo thứ tự input; index trong từng phần tử
        # cũng map về vị trí. Sắp lại theo ``index`` cho an toàn.
        ordered = sorted(data, key=lambda d: d.get("index", 0))
        vectors: list[list[float]] = []
        for item in ordered:
            embedding = item.get("embedding")
            if embedding is None:
                raise RuntimeError(
                    "OpenAI embeddings response thiếu field 'embedding'."
                )
            vectors.append([float(x) for x in embedding])
        return vectors

    async def embed_one(self, text: str) -> list[float]:
        vectors = await self._post_embeddings([text])
        return vectors[0]

    async def embed_many(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        return await self._post_embeddings(list(texts))


# ---------------------------------------------------------------------------
# EmbeddingService (cache wrapper)
# ---------------------------------------------------------------------------


def _embedding_cache_key(provider: str, text: str) -> str:
    """Trả về cache key theo convention design (Requirement 6.1).

    Format: ``embed:{provider}:{sha256(text)}``.
    """
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return f"embed:{provider}:{digest}"


# TTL mặc định khi caller không truyền (Requirement 6.2).
_DEFAULT_EMBEDDING_TTL_SECONDS: int = 3600


class EmbeddingService:
    """Public façade dùng bởi RAG_Service / Indexing_Job.

    Bọc ``EmbeddingBackend`` với cache layer:

    * :meth:`embed` đi qua cache (key + TTL theo design).
    * :meth:`embed_batch` không qua cache đơn lẻ — Indexing_Job xử lý số
      lượng lớn, chia theo batch mà cache embedding ngắn hạn không có giá
      trị (mỗi chunk thường là duy nhất). Hành vi này khớp design note
      ở task 6.5.
    * :attr:`dimension` delegate xuống backend để consumer biết kích thước
      vector cần (cho pgvector schema).
    """

    def __init__(
        self,
        provider: str,
        backend: EmbeddingBackend,
        cache: CacheManager,
        *,
        ttl_seconds: int = _DEFAULT_EMBEDDING_TTL_SECONDS,
    ) -> None:
        if not provider:
            raise ValueError("EmbeddingService yêu cầu provider non-empty.")
        if ttl_seconds <= 0:
            raise ValueError(
                f"ttl_seconds phải > 0, nhận {ttl_seconds}."
            )
        self._provider = provider
        self._backend = backend
        self._cache = cache
        self._ttl_seconds = ttl_seconds

    @property
    def provider(self) -> str:
        return self._provider

    @property
    def dimension(self) -> int:
        return self._backend.dimension

    async def embed(self, text: str) -> list[float]:
        """Embed một text qua cache (Requirements 4.1, 6.1, 6.2)."""
        key = _embedding_cache_key(self._provider, text)
        cached = self._cache.get(key)
        if cached is not None:
            # Defensive copy để caller mutate không corrupt cache state.
            return list(cached)
        vector = await self._backend.embed_one(text)
        # Lưu list (immutable theo convention; cache layer giữ reference).
        self._cache.set(key, list(vector), ttl_seconds=self._ttl_seconds)
        return vector

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Batch embed cho Indexing_Job — bypass per-item cache."""
        if not texts:
            return []
        return await self._backend.embed_many(list(texts))


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_embedding_service(settings: Any, cache: CacheManager) -> EmbeddingService:
    """Khởi tạo ``EmbeddingService`` theo ``settings.EMBEDDING_PROVIDER``.

    Chọn backend:

    * ``"local"`` → :class:`LocalSentenceTransformerEmbedder` (384d).
    * ``"openai"`` → :class:`OpenAIEmbedder` (1536d), cần ``OPENAI_API_KEY``.

    TTL lấy từ ``settings.CACHE_TTL_EMBEDDING_SECONDS`` nếu được set
    (Requirement 6.2 cho phép operator override qua env), fallback 3600.
    Dimension lấy từ ``settings.EMBEDDING_DIMENSION`` nếu khớp backend; nếu
    operator cấu hình lệch (vd local + 1536) thì raise ``ValueError`` để
    fail fast trước khi chạy migration vector schema.
    """
    provider = getattr(settings, "EMBEDDING_PROVIDER", None)
    if provider not in ("local", "openai"):
        raise ValueError(
            f"EMBEDDING_PROVIDER không hợp lệ: {provider!r}. "
            "Chỉ chấp nhận 'local' hoặc 'openai'."
        )

    configured_dim = getattr(settings, "EMBEDDING_DIMENSION", None)
    ttl_seconds = int(
        getattr(settings, "CACHE_TTL_EMBEDDING_SECONDS", _DEFAULT_EMBEDDING_TTL_SECONDS)
        or _DEFAULT_EMBEDDING_TTL_SECONDS
    )

    backend: EmbeddingBackend
    if provider == "local":
        expected = LocalSentenceTransformerEmbedder.DEFAULT_DIMENSION
        if configured_dim is not None and int(configured_dim) != expected:
            raise ValueError(
                f"EMBEDDING_DIMENSION={configured_dim} không khớp backend "
                f"local (yêu cầu {expected})."
            )
        backend = LocalSentenceTransformerEmbedder(dimension=expected)
    else:  # openai
        api_key = getattr(settings, "OPENAI_API_KEY", "") or ""
        if not api_key:
            raise ValueError(
                "EMBEDDING_PROVIDER=openai nhưng OPENAI_API_KEY trống."
            )
        expected = OpenAIEmbedder.DEFAULT_DIMENSION
        if configured_dim is not None and int(configured_dim) != expected:
            raise ValueError(
                f"EMBEDDING_DIMENSION={configured_dim} không khớp backend "
                f"openai (yêu cầu {expected})."
            )
        timeout = float(getattr(settings, "LLM_TIMEOUT_SECONDS", 30) or 30)
        backend = OpenAIEmbedder(
            api_key=api_key,
            dimension=expected,
            timeout_seconds=timeout,
        )

    return EmbeddingService(
        provider=provider,
        backend=backend,
        cache=cache,
        ttl_seconds=ttl_seconds,
    )
