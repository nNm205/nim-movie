# Feature: ai-chatbot-rag, Property 7: Review chunking bounds. Mọi chunk ≤ 512 tokens; hai chunk liên tiếp share đúng 50 tokens; metadata chứa movie_id, rating, review_id
"""Property-based test cho Document_Chunker.chunk_review.

**Validates: Requirements 3.5**

Property 7 (theo design.md / tasks.md): với mọi review payload có
``review_text`` mà encoded length ``n ∈ [1, 5000]`` token (cl100k_base),
``chunk_review(review)`` trả về danh sách chunk ``cs`` thoả:

1. Mỗi chunk ``c_i`` có ``len(tokens(c_i)) ≤ 512``.
2. Với hai chunk liên tiếp ``c_i`` và ``c_{i+1}``:
   ``tokens(c_i)[-50:] == tokens(c_{i+1})[:50]`` — share đúng 50 token.
3. ``metadata`` của mỗi chunk chứa ba key ``movie_id``, ``rating``,
   ``review_id`` với giá trị trùng đúng input review.

Strategy: ``review_text`` được build bằng cách concat random ASCII word rồi
slice ở token boundary tới target length ``n ∈ [1, 5000]``. Dùng ASCII-safe
text để đảm bảo decode → re-encode round-trip ổn định ở cl100k_base BPE
(cùng convention như ``test_movie_chunking_property.py``); test này nhắm
shape/bounds của chunker chứ không phải robustness của tokenizer trên
unicode đầy đủ.
"""

from __future__ import annotations

import tiktoken
from hypothesis import given, settings
from hypothesis import strategies as st

from app.services.ai.embeddings import chunk_review

# Encoder dùng chung — cl100k_base, đúng với encoder mà ``chunk_text`` dùng
# cho boundary 512 token / overlap 50 token.
_ENCODER = tiktoken.get_encoding("cl100k_base")


# ---- Strategies -------------------------------------------------------------

# Pool từ ASCII đơn giản; mỗi từ ≈ 1-2 token cl100k_base. Đa dạng đủ để
# token sequence không trivial nhưng round-trip ổn định.
_WORD_POOL = (
    "the",
    "movie",
    "is",
    "really",
    "great",
    "and",
    "well",
    "acted",
    "story",
    "plot",
    "scene",
    "actor",
    "director",
    "good",
    "bad",
    "amazing",
    "boring",
    "interesting",
    "very",
    "much",
    "this",
    "that",
    "film",
    "was",
    "were",
    "had",
    "with",
    "about",
    "love",
    "hate",
    "watch",
    "saw",
    "year",
    "long",
    "short",
)


@st.composite
def _review_text_strategy(draw: st.DrawFn) -> tuple[str, int]:
    """Sinh ``review_text`` ASCII có encoded length ∈ [1, 5000] tokens.

    Trả về tuple ``(text, n_tokens)`` để assertion có thể đối chiếu mong đợi
    về số chunk mà không phải re-encode lần nữa.
    """
    n_tokens = draw(st.integers(min_value=1, max_value=5000))
    # Build text dài hơn target (ASCII word pool) rồi slice ở token boundary
    # để đạt chính xác n_tokens. Nhân hệ số 4 (≈ ký tự / từ × token / từ
    # ngược lại) để chắc chắn đủ token.
    words = draw(
        st.lists(
            st.sampled_from(_WORD_POOL),
            min_size=max(1, n_tokens),
            max_size=max(1, n_tokens) * 4,
        )
    )
    raw = " ".join(words)
    tokens = _ENCODER.encode(raw)
    # Đảm bảo đủ token; nếu không đủ (xác suất rất thấp với min_size trên),
    # pad bằng cách lặp lại pool.
    while len(tokens) < n_tokens:
        raw = raw + " " + " ".join(_WORD_POOL)
        tokens = _ENCODER.encode(raw)
    text = _ENCODER.decode(tokens[:n_tokens])
    # Re-encode để chắc chắn token count đúng n_tokens (ASCII pool round-trip
    # ổn định — verify sanity).
    assert len(_ENCODER.encode(text)) == n_tokens
    return text, n_tokens


@st.composite
def _review_strategy(draw: st.DrawFn) -> dict:
    """Sinh review payload dạng dict cho ``chunk_review``.

    Field theo Requirement 3.5:
    ``id`` (review_id), ``movie_id``, ``rating``, ``review_text``.
    """
    text, n_tokens = draw(_review_text_strategy())
    return {
        "id": draw(st.integers(min_value=1, max_value=10**9)),
        "movie_id": draw(st.integers(min_value=1, max_value=10**9)),
        "rating": draw(st.integers(min_value=1, max_value=10)),
        "review_text": text,
        "_n_tokens": n_tokens,
    }


# ---- Property test ----------------------------------------------------------


@given(review=_review_strategy())
@settings(max_examples=50, deadline=None)
def test_chunk_review_bounds_and_metadata(review: dict) -> None:
    # Feature: ai-chatbot-rag, Property 7: Review chunking bounds. Mọi chunk ≤ 512 tokens; hai chunk liên tiếp share đúng 50 tokens; metadata chứa movie_id, rating, review_id
    """**Validates: Requirements 3.5**"""

    # Tách meta-field ``_n_tokens`` trước khi đẩy vào chunk_review.
    expected_n_tokens = review["_n_tokens"]
    payload = {k: v for k, v in review.items() if not k.startswith("_")}

    chunks = chunk_review(payload)

    # ---- Pre-condition: review có review_text non-empty ⇒ ≥ 1 chunk -------
    assert len(chunks) >= 1, "review_text non-empty phải sinh ≥ 1 chunk"

    # ---- 1. Mọi chunk ≤ 512 tokens ----------------------------------------
    encoded_chunks: list[list[int]] = []
    for c in chunks:
        toks = _ENCODER.encode(c["content"])
        encoded_chunks.append(toks)
        assert len(toks) <= 512, (
            f"Chunk {c['chunk_index']} có {len(toks)} tokens > 512"
        )

    # ---- 2. Hai chunk liên tiếp share đúng 50 tokens overlap --------------
    # Chỉ áp dụng khi có ≥ 2 chunk (tức review_text > 512 token gốc).
    if len(encoded_chunks) >= 2:
        for i in range(len(encoded_chunks) - 1):
            prev_tail = encoded_chunks[i][-50:]
            next_head = encoded_chunks[i + 1][:50]
            assert prev_tail == next_head, (
                f"Chunk {i} và {i + 1} không share đúng 50 tokens overlap. "
                f"prev_tail (len={len(prev_tail)}) != next_head "
                f"(len={len(next_head)})"
            )
        # Số chunk khớp công thức sliding window:
        # ceil((n - overlap) / (max - overlap)) = ceil((n - 50) / 462).
        if expected_n_tokens > 512:
            stride = 512 - 50  # 462
            expected_count = 1 + -((-(expected_n_tokens - 512)) // stride)
            assert len(chunks) == expected_count, (
                f"Số chunk = {len(chunks)}, expected {expected_count} cho "
                f"n_tokens={expected_n_tokens}"
            )

    # ---- 3. Metadata chứa movie_id, rating, review_id ---------------------
    for c in chunks:
        meta = c["metadata"]
        for required_key in ("movie_id", "rating", "review_id"):
            assert required_key in meta, (
                f"Chunk {c['chunk_index']} metadata thiếu key {required_key!r}: "
                f"{meta!r}"
            )
        # Giá trị metadata phải khớp đúng input review.
        assert meta["movie_id"] == payload["movie_id"]
        assert meta["rating"] == payload["rating"]
        assert meta["review_id"] == payload["id"]

    # ---- chunk_index liên tục 0..n-1 (sanity, không phải property chính) --
    indices = [c["chunk_index"] for c in chunks]
    assert indices == list(range(len(chunks)))


# ---- Edge cases sanity (deterministic) -------------------------------------


def test_chunk_review_short_text_fits_single_chunk() -> None:
    # Feature: ai-chatbot-rag, Property 7: Review chunking bounds. Mọi chunk ≤ 512 tokens; hai chunk liên tiếp share đúng 50 tokens; metadata chứa movie_id, rating, review_id
    """**Validates: Requirements 3.5** — review ngắn (< 512 token) ⇒ 1 chunk."""
    review = {
        "id": 42,
        "movie_id": 7,
        "rating": 9,
        "review_text": "Phim hay tuyệt vời, diễn xuất đỉnh.",
    }
    chunks = chunk_review(review)
    assert len(chunks) == 1
    assert chunks[0]["chunk_index"] == 0
    meta = chunks[0]["metadata"]
    assert meta["movie_id"] == 7
    assert meta["rating"] == 9
    assert meta["review_id"] == 42


def test_chunk_review_empty_text_returns_no_chunks() -> None:
    # Feature: ai-chatbot-rag, Property 7: Review chunking bounds. Mọi chunk ≤ 512 tokens; hai chunk liên tiếp share đúng 50 tokens; metadata chứa movie_id, rating, review_id
    """**Validates: Requirements 3.5** — ``review_text`` rỗng/None ⇒ ``[]``."""
    assert chunk_review({"id": 1, "movie_id": 1, "rating": 5, "review_text": None}) == []
    assert chunk_review({"id": 1, "movie_id": 1, "rating": 5, "review_text": ""}) == []
    assert chunk_review({"id": 1, "movie_id": 1, "rating": 5, "review_text": "   "}) == []


def test_chunk_review_long_text_consecutive_chunks_share_50_tokens() -> None:
    # Feature: ai-chatbot-rag, Property 7: Review chunking bounds. Mọi chunk ≤ 512 tokens; hai chunk liên tiếp share đúng 50 tokens; metadata chứa movie_id, rating, review_id
    """**Validates: Requirements 3.5** — review ~3000 token ⇒ multi-chunk overlap 50."""
    text = " ".join(["the movie is really great"] * 800)
    review = {"id": 100, "movie_id": 200, "rating": 8, "review_text": text}
    chunks = chunk_review(review)
    assert len(chunks) >= 2
    encoded = [_ENCODER.encode(c["content"]) for c in chunks]
    for toks in encoded:
        assert len(toks) <= 512
    for i in range(len(encoded) - 1):
        assert encoded[i][-50:] == encoded[i + 1][:50]
        # Mỗi chunk trừ chunk cuối phải đầy 512 token.
        assert len(encoded[i]) == 512
    for c in chunks:
        meta = c["metadata"]
        assert meta["movie_id"] == 200
        assert meta["rating"] == 8
        assert meta["review_id"] == 100
