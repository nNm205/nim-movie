"""Unit test cho ``EmbeddingService`` × ``InMemoryCacheManager`` integration.

**Validates: Requirements 6.1, 6.2**

Theo design / implementation hiện tại của
``app/services/ai/embeddings.py``:

* ``EmbeddingService.embed(text)`` đi qua cache với key
  ``embed:{provider}:{sha256(text)}`` (Requirement 6.1) và TTL mặc định
  3600s (Requirement 6.2).
* ``EmbeddingService.embed_batch(texts)`` **bypass** per-item cache —
  trích nguyên văn docstring trong code:

      "Batch embed cho Indexing_Job — bypass per-item cache."

  Lý do design (cũng có note ở task 6.5): Indexing_Job xử lý số lượng
  lớn chunk thường là duy nhất, cache embedding ngắn hạn không có giá
  trị; ngoài ra giữ batch path đơn giản giúp throughput tốt hơn.

Các test dưới đây dùng ``InMemoryCacheManager`` thật (không mock cache
layer) để exercise đúng cache integration; chỉ mock phần "model" — tức
là backend ``embed_one`` / ``embed_many`` (hoặc với một test, là
``model.encode`` của ``LocalSentenceTransformerEmbedder``).
"""

from __future__ import annotations

import hashlib
from typing import Any
from unittest.mock import MagicMock

import pytest

from app.integrations.cache_manager import InMemoryCacheManager
from app.services.ai.embeddings import (
    EmbeddingService,
    LocalSentenceTransformerEmbedder,
    _embedding_cache_key,
)


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------


class FakeBackend:
    """Backend giả implement ``EmbeddingBackend`` Protocol, đếm số call.

    - ``embed_one`` đếm vào ``one_calls`` và lưu danh sách input.
    - ``embed_many`` đếm vào ``many_calls`` và lưu danh sách batch input.
    - Vector trả về deterministic theo ``len(text)`` để dễ assert.
    """

    def __init__(self, dimension: int = 4) -> None:
        self._dimension = dimension
        self.one_calls: list[str] = []
        self.many_calls: list[list[str]] = []

    @property
    def dimension(self) -> int:
        return self._dimension

    @staticmethod
    def _vector_for(text: str, dimension: int) -> list[float]:
        # Vector giả deterministic: [len(text), len(text)+1, ...].
        base = float(len(text))
        return [base + float(i) for i in range(dimension)]

    async def embed_one(self, text: str) -> list[float]:
        self.one_calls.append(text)
        return self._vector_for(text, self._dimension)

    async def embed_many(self, texts: list[str]) -> list[list[float]]:
        # Defensive copy để giữ snapshot input độc lập với caller.
        self.many_calls.append(list(texts))
        return [self._vector_for(t, self._dimension) for t in texts]


@pytest.fixture
def cache() -> Any:
    """Cache thật, sweep tắt để test deterministic, dọn dẹp sau mỗi test."""
    c = InMemoryCacheManager(sweep_interval_seconds=0)
    try:
        yield c
    finally:
        c.shutdown()


@pytest.fixture
def backend() -> FakeBackend:
    return FakeBackend(dimension=4)


@pytest.fixture
def service(cache: InMemoryCacheManager, backend: FakeBackend) -> EmbeddingService:
    return EmbeddingService(provider="local", backend=backend, cache=cache)


# ---------------------------------------------------------------------------
# Cache hit/miss cho ``embed`` (Requirements 6.1, 6.2)
# ---------------------------------------------------------------------------


class TestEmbedCacheHit:
    """``EmbeddingService.embed`` phải cache theo (provider, sha256(text))."""

    @pytest.mark.asyncio
    async def test_second_call_same_text_uses_cache(
        self, service: EmbeddingService, backend: FakeBackend
    ) -> None:
        """Hai lần ``embed("hello")`` → backend gọi đúng 1 lần."""
        first = await service.embed("hello")
        second = await service.embed("hello")

        assert backend.one_calls == ["hello"], (
            "Second call should be served from cache, "
            f"but backend was called {len(backend.one_calls)} times."
        )
        # Vector trả về 2 lần phải bằng nhau (cache trả đúng giá trị đã lưu).
        assert second == first

    @pytest.mark.asyncio
    async def test_cache_returns_defensive_copy(
        self, service: EmbeddingService, backend: FakeBackend
    ) -> None:
        """Mutate kết quả lần 1 không corrupt entry cache cho lần 2."""
        first = await service.embed("hello")
        first_snapshot = list(first)

        # Caller mutate kết quả trả về.
        first.append(999.0)

        second = await service.embed("hello")
        # Backend vẫn chỉ được gọi 1 lần (cache hit).
        assert backend.one_calls == ["hello"]
        # Cache trả về dữ liệu nguyên vẹn, không bị poison.
        assert second == first_snapshot

    @pytest.mark.asyncio
    async def test_different_texts_each_miss(
        self, service: EmbeddingService, backend: FakeBackend
    ) -> None:
        """``embed("hello")`` rồi ``embed("world")`` → backend gọi 2 lần."""
        await service.embed("hello")
        await service.embed("world")

        assert backend.one_calls == ["hello", "world"]

    @pytest.mark.asyncio
    async def test_cache_key_format_matches_design(
        self,
        service: EmbeddingService,
        cache: InMemoryCacheManager,
    ) -> None:
        """Key trong cache đúng format ``embed:{provider}:{sha256(text)}``.

        Ràng buộc trực tiếp Requirement 6.1: key convention.
        """
        text = "hello"
        await service.embed(text)

        expected_key = (
            f"embed:local:"
            f"{hashlib.sha256(text.encode('utf-8')).hexdigest()}"
        )
        # Helper public-ish của module phải trả đúng cùng key.
        assert _embedding_cache_key("local", text) == expected_key
        # Cache thật chứa entry với key đó.
        assert cache.get(expected_key) is not None


# ---------------------------------------------------------------------------
# Cách ly cache theo provider (Requirement 6.1)
# ---------------------------------------------------------------------------


class TestProviderIsolation:
    """Hai service khác provider nhưng share cùng ``CacheManager`` không
    được nhầm cache entry của nhau (key có prefix provider)."""

    @pytest.mark.asyncio
    async def test_different_providers_do_not_share_cache(
        self, cache: InMemoryCacheManager
    ) -> None:
        backend_local = FakeBackend(dimension=4)
        backend_openai = FakeBackend(dimension=4)
        svc_local = EmbeddingService(
            provider="local", backend=backend_local, cache=cache
        )
        svc_openai = EmbeddingService(
            provider="openai", backend=backend_openai, cache=cache
        )

        # Warm cache từ phía "local".
        await svc_local.embed("hello")
        # Service "openai" KHÔNG được hit cache của "local".
        await svc_openai.embed("hello")

        assert backend_local.one_calls == ["hello"]
        assert backend_openai.one_calls == ["hello"], (
            "openai service must not reuse cache entry written by local "
            "service — provider is part of the cache key."
        )

        # Lần thứ hai của từng service vẫn HIT cache của chính nó.
        await svc_local.embed("hello")
        await svc_openai.embed("hello")
        assert backend_local.one_calls == ["hello"]
        assert backend_openai.one_calls == ["hello"]


# ---------------------------------------------------------------------------
# ``embed_batch`` bypass per-item cache (theo design)
# ---------------------------------------------------------------------------


class TestEmbedBatchBypassesPerItemCache:
    """Theo design (xem docstring ``EmbeddingService.embed_batch``):

        "Batch embed cho Indexing_Job — bypass per-item cache."

    Tức là batch path không đọc / ghi vào cache embedding của
    ``embed(text)``. Hai test dưới khoá hành vi này từ cả hai phía.
    """

    @pytest.mark.asyncio
    async def test_warm_cache_then_batch_still_calls_backend_many(
        self, service: EmbeddingService, backend: FakeBackend
    ) -> None:
        """``embed("hello")`` warm cache, nhưng ``embed_batch(["hello"])``
        vẫn phải gọi ``backend.embed_many(["hello"])``."""
        await service.embed("hello")
        assert backend.one_calls == ["hello"]
        assert backend.many_calls == []

        result = await service.embed_batch(["hello"])

        # Batch không lấy từ cache — backend.embed_many bị gọi với input
        # nguyên vẹn (kể cả phần tử "hello" đã có trong cache).
        assert backend.many_calls == [["hello"]]
        # ``embed_one`` không bị gọi thêm — batch path là code path khác.
        assert backend.one_calls == ["hello"]
        # Vector trả về phải đúng kích thước batch.
        assert len(result) == 1
        assert len(result[0]) == backend.dimension

    @pytest.mark.asyncio
    async def test_batch_does_not_warm_per_item_cache(
        self, service: EmbeddingService, backend: FakeBackend
    ) -> None:
        """``embed_batch(["hello"])`` không ghi vào cache ⇒ ``embed("hello")``
        sau đó vẫn MISS và gọi ``embed_one``."""
        await service.embed_batch(["hello"])
        assert backend.many_calls == [["hello"]]
        assert backend.one_calls == []

        await service.embed("hello")

        # Batch path không warm cache → embed phải compute lại qua embed_one.
        assert backend.one_calls == ["hello"]

    @pytest.mark.asyncio
    async def test_empty_batch_short_circuits(
        self, service: EmbeddingService, backend: FakeBackend
    ) -> None:
        """``embed_batch([])`` phải trả ``[]`` mà không gọi backend."""
        result = await service.embed_batch([])
        assert result == []
        assert backend.many_calls == []
        assert backend.one_calls == []


# ---------------------------------------------------------------------------
# Mock trực tiếp ``model.encode`` qua LocalSentenceTransformerEmbedder
# ---------------------------------------------------------------------------


class TestModelEncodeMockedThroughLocalBackend:
    """Bám sát đề bài task 6.5: "Mock ``model.encode``, gọi ``embed("hello")``
    2 lần liên tiếp → model gọi đúng 1 lần, lần 2 từ cache."

    ``LocalSentenceTransformerEmbedder._encode_sync`` là nơi gọi
    ``model.encode``. Ta patch ``_load_model`` trên instance để trả về một
    ``MagicMock`` có ``.encode``; cache layer thật sẽ ngăn lần thứ 2 đi
    xuống tới ``encode``.
    """

    @pytest.mark.asyncio
    async def test_model_encode_called_once_for_repeated_embed(
        self, cache: InMemoryCacheManager, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        backend = LocalSentenceTransformerEmbedder()

        # Mock model: ``.encode(texts, ...)`` trả về list-of-list float
        # giống ndarray.tolist() để ``_encode_sync`` xử lý suôn sẻ.
        fake_model = MagicMock(name="FakeSentenceTransformer")
        fake_model.encode.return_value = [[0.1, 0.2, 0.3] + [0.0] * 381]

        # Patch ``_load_model`` của instance để bỏ qua import / weights load.
        monkeypatch.setattr(backend, "_load_model", lambda: fake_model)

        service = EmbeddingService(
            provider="local", backend=backend, cache=cache
        )

        first = await service.embed("hello")
        second = await service.embed("hello")

        assert fake_model.encode.call_count == 1, (
            "Lần thứ 2 phải hit cache; model.encode chỉ được gọi 1 lần. "
            f"Thực tế: {fake_model.encode.call_count}."
        )
        assert second == first
