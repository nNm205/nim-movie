# Feature: ai-chatbot-rag, Property 19: Embedding cache hit/miss trong TTL. Lần đầu miss, các lần trong TTL hit, sau TTL miss lại
"""Property-based test cho Embedding cache TTL.

**Validates: Requirements 6.1, 6.2**

Theo design, ``EmbeddingService.embed(text)`` đi qua ``Cache_Manager`` với:

- Key: ``embed:{provider}:{sha256(text)}``  (Requirement 6.1)
- TTL: 3600 giây                            (Requirement 6.2)

Property 19: với mọi ``text`` và mọi sequence ``deltas`` của timedeltas
(theo giây) áp dụng nối tiếp lên đồng hồ, hành vi của cache phải là:

1. Lần đầu hoặc khi entry đã expired (now ≥ expires_at) → **MISS**: hàm
   compute bên dưới được gọi đúng một lần và cache được refresh với
   ``expires_at = now + 3600``.
2. Các lần truy cập trong cửa sổ TTL (now < expires_at) → **HIT**: hàm
   compute KHÔNG được gọi.

Test invariant: ``compute_calls == expected_miss_count`` cho mọi
``(text, deltas)``.

Cách inject fake clock: thay attribute ``time`` của module
``app.integrations.cache_manager`` bằng một ``SimpleNamespace`` chứa
``monotonic = clock.now``. Cách này giữ ``time.monotonic`` toàn cục
nguyên vẹn (an toàn cho test chạy song song) và phục vụ tốt cho
``InMemoryCacheManager`` vốn gọi ``time.monotonic()`` qua reference module.
"""

from __future__ import annotations

import hashlib
import types

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from app.integrations import cache_manager as cache_manager_module
from app.integrations.cache_manager import InMemoryCacheManager

# Hằng số khớp design (Requirement 6.2 và embed key convention).
EMBEDDING_TTL_SECONDS: int = 3600
PROVIDER: str = "test-provider"


class FakeClock:
    """Đồng hồ giả injectable, đo thời gian theo giây trên float monotonic."""

    def __init__(self, start: float = 1000.0) -> None:
        self._now = float(start)

    def now(self) -> float:
        return self._now

    def advance(self, seconds: float) -> None:
        # Float không âm — strategy đã ràng buộc, nhưng vẫn defensive.
        if seconds < 0:
            seconds = 0.0
        self._now += float(seconds)


def _embedding_key(text: str, provider: str = PROVIDER) -> str:
    """Tái tạo cache key của ``EmbeddingService.embed`` (Requirement 6.1)."""
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return f"embed:{provider}:{digest}"


# ---- Strategies -------------------------------------------------------------


def _text_strategy() -> st.SearchStrategy[str]:
    """Sinh ``text`` đầu vào: unicode tùy ý, kể cả rỗng và ký tự đặc biệt.

    Giới hạn ``max_size=128`` đủ để cover practical user message; key của
    cache là ``sha256`` nên độ dài text không ảnh hưởng đến TTL property.
    """
    return st.text(min_size=0, max_size=128)


def _delta_strategy() -> st.SearchStrategy[float]:
    """Sinh timedelta (giây) ∈ [0, 7200].

    Khoảng [0, 7200] cover cả các bước < TTL (giữ HIT), bước đúng = TTL
    (boundary expired), và bước > TTL (force MISS). Floats cho phép kiểm
    biên với phần thập phân quanh 3600.0.
    """
    return st.floats(
        min_value=0.0,
        max_value=7200.0,
        allow_nan=False,
        allow_infinity=False,
    )


# ---- Property test ----------------------------------------------------------


@given(
    text=_text_strategy(),
    deltas=st.lists(_delta_strategy(), min_size=1, max_size=20),
)
@settings(
    max_examples=150,
    deadline=None,
    # ``monkeypatch`` is function-scoped and we intentionally re-apply the
    # fake clock + spin up a fresh ``InMemoryCacheManager`` inside the test
    # body for each generated input, so cross-example state leakage cannot
    # happen. Suppress the health check that warns about the pattern.
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
def test_embedding_cache_ttl_hit_miss(
    monkeypatch: pytest.MonkeyPatch,
    text: str,
    deltas: list[float],
) -> None:
    # Feature: ai-chatbot-rag, Property 19: Embedding cache hit/miss trong TTL. Lần đầu miss, các lần trong TTL hit, sau TTL miss lại
    """**Validates: Requirements 6.1, 6.2**

    Với mọi ``text`` và mọi sequence ``deltas``, số lần ``compute`` thực sự
    được gọi phải bằng số MISS dự kiến tính theo cửa sổ TTL trên fake clock.
    """
    # Inject fake clock vào module ``cache_manager``: thay reference ``time``
    # bằng SimpleNamespace có ``monotonic`` trỏ tới fake. Không động vào
    # ``time.monotonic`` toàn cục.
    clock = FakeClock(start=1000.0)
    fake_time_module = types.SimpleNamespace(monotonic=clock.now)
    monkeypatch.setattr(cache_manager_module, "time", fake_time_module)

    # ``sweep_interval_seconds=0`` để bỏ qua daemon thread; test deterministic
    # không phụ thuộc vào periodic sweep.
    cache = InMemoryCacheManager(sweep_interval_seconds=0)
    try:
        # Counter cho compute function bên dưới (mô phỏng ``model.encode``).
        compute_calls = 0

        def cached_embed(s: str) -> list[float]:
            """Mô phỏng ``EmbeddingService.embed(text)`` đi qua cache.

            Tăng counter mỗi lần MISS, không tăng khi HIT.
            """
            nonlocal compute_calls
            key = _embedding_key(s)
            cached = cache.get(key)
            if cached is not None:
                return cached  # HIT
            compute_calls += 1
            # Embedding "thật" không quan trọng cho property này; chỉ cần
            # deterministic + có thể equality-check khi cần. Dùng len(s) để
            # tránh phụ thuộc model thật.
            value = [float(len(s))]
            cache.set(key, value, ttl_seconds=EMBEDDING_TTL_SECONDS)
            return value

        # Mô hình kỳ vọng: track ``expected_expires_at`` của entry hiện tại
        # (None khi cache chưa có entry hợp lệ). Logic đúng phải khớp với
        # ``InMemoryCacheManager``: entry hết hạn khi ``expires_at <= now``.
        expected_expires_at: float | None = None
        expected_miss_count = 0

        for d in deltas:
            clock.advance(d)
            now = clock.now()

            if expected_expires_at is None or expected_expires_at <= now:
                # MISS: tính lại và refresh expires_at (set sau compute).
                expected_miss_count += 1
                expected_expires_at = now + EMBEDDING_TTL_SECONDS
            # else: HIT — expected_expires_at giữ nguyên.

            # Gọi cached_embed với cùng text → cùng key → cùng entry.
            cached_embed(text)

        # Property: số compute thực tế khớp số MISS kỳ vọng.
        assert compute_calls == expected_miss_count, (
            "Embedding cache vi phạm Property 19: "
            f"compute_calls={compute_calls} != expected_miss_count="
            f"{expected_miss_count} (deltas={deltas!r})"
        )
    finally:
        cache.shutdown()


# ---- Sanity checks (concrete examples) -------------------------------------


def test_embedding_cache_first_call_misses_subsequent_within_ttl_hit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Feature: ai-chatbot-rag, Property 19: Embedding cache hit/miss trong TTL. Lần đầu miss, các lần trong TTL hit, sau TTL miss lại
    """**Validates: Requirements 6.1, 6.2**

    Sanity: lần đầu MISS, hai lần kế tiếp trong TTL HIT, sau TTL MISS lại.
    """
    clock = FakeClock(start=0.0)
    monkeypatch.setattr(
        cache_manager_module,
        "time",
        types.SimpleNamespace(monotonic=clock.now),
    )

    cache = InMemoryCacheManager(sweep_interval_seconds=0)
    try:
        compute_calls = 0

        def cached_embed(s: str) -> list[float]:
            nonlocal compute_calls
            key = _embedding_key(s)
            v = cache.get(key)
            if v is not None:
                return v
            compute_calls += 1
            v = [float(len(s))]
            cache.set(key, v, ttl_seconds=EMBEDDING_TTL_SECONDS)
            return v

        text = "phim hành động Hàn Quốc"

        # Lần 1: MISS.
        cached_embed(text)
        assert compute_calls == 1

        # Trong TTL: HIT.
        clock.advance(1000)
        cached_embed(text)
        assert compute_calls == 1

        clock.advance(2599.999)  # tổng = 3599.999 < 3600 → vẫn HIT
        cached_embed(text)
        assert compute_calls == 1

        # Tới thời điểm 3600.0: entry hết hạn (expires_at <= now) → MISS.
        clock.advance(0.001)
        cached_embed(text)
        assert compute_calls == 2

        # Trong TTL mới: HIT.
        clock.advance(10)
        cached_embed(text)
        assert compute_calls == 2

        # Quá TTL mới: MISS lại.
        clock.advance(EMBEDDING_TTL_SECONDS + 1)
        cached_embed(text)
        assert compute_calls == 3
    finally:
        cache.shutdown()
