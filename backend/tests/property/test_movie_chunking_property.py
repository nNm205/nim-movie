# Feature: ai-chatbot-rag, Property 6: Movie chunking shape. Đúng 1 chunk index 0 với pattern summary; min(k,10) cast top + director; mọi chunk ≤ 512 tokens
"""Property-based test cho Document_Chunker.chunk_movie.

**Validates: Requirements 3.4**

Property 6 (theo design.md): với mọi TMDBMovie ``m`` có ``cast`` size
``k ∈ [0, 50]``, ``chunk_movie(m)`` trả về list chunks thoả:

1. Có **chính xác 1** chunk với ``chunk_index == 0`` và ``content`` khớp
   pattern ``"{title} ({year}) - {genres_csv}. {overview}"``.
2. Các chunk còn lại (cast/director) tổng cộng bằng
   ``min(k, 10) + (1 if director else 0)``.
3. Không có chunk nào có ``len(tokens) > 512`` (đo bằng ``tiktoken`` encoding
   ``cl100k_base``).

Strategy: TMDBMovie payload kiểu dict TMDb thô (như ``chunk_movie`` ăn vào)
với cast size random trong ``[0, 50]``, năm 4 số, genres 0..5 tên, tiêu đề /
overview / character giới hạn ASCII printable để giữ token count bounded
(test này nhắm shape, không phải unicode robustness).
"""

from __future__ import annotations

import tiktoken
from hypothesis import given, settings
from hypothesis import strategies as st

from app.services.ai.embeddings import chunk_movie

# Encoder dùng chung — khởi tạo một lần ở module level (cl100k_base, đúng
# với encoder mà ``chunk_text`` đang dùng cho boundary 512 token).
_ENCODER = tiktoken.get_encoding("cl100k_base")


# ---- Strategies -------------------------------------------------------------

# ASCII printable không chứa ký tự điều khiển; giúp token count predictable
# (cl100k_base ~0.25 token/char cho English ASCII) nên tổng summary luôn fit
# 512 token với các bound bên dưới.
_ASCII_TEXT = st.text(
    alphabet=st.characters(min_codepoint=32, max_codepoint=126),
    max_size=50,
)
_ASCII_LONG = st.text(
    alphabet=st.characters(min_codepoint=32, max_codepoint=126),
    max_size=300,
)
_ASCII_NAME = st.text(
    alphabet=st.characters(min_codepoint=65, max_codepoint=122),
    min_size=1,
    max_size=20,
)


@st.composite
def tmdb_movie_strategy(draw: st.DrawFn) -> dict:
    """Sinh TMDBMovie payload (dict TMDb thô) với cast size ∈ [0, 50].

    Mỗi cast member luôn có ``name`` non-empty (để cast chunk không bị
    chunker skip — implementation bỏ qua cast member rỗng tên, xem
    ``chunk_movie`` trong ``app/services/ai/embeddings.py``). Director
    optional theo flag.
    """
    title = draw(st.text(
        alphabet=st.characters(min_codepoint=32, max_codepoint=126),
        min_size=1,
        max_size=50,
    ))
    year = draw(st.integers(min_value=1900, max_value=2100))
    overview = draw(_ASCII_LONG)

    genre_names = draw(
        st.lists(
            st.sampled_from(
                [
                    "Action",
                    "Drama",
                    "Comedy",
                    "Thriller",
                    "Romance",
                    "Sci-Fi",
                    "Horror",
                    "Adventure",
                    "Animation",
                    "Mystery",
                ]
            ),
            min_size=0,
            max_size=5,
            unique=True,
        )
    )

    cast_size = draw(st.integers(min_value=0, max_value=50))
    cast = []
    for i in range(cast_size):
        cast.append(
            {
                "id": 10_000 + i,
                "name": f"Actor {i}",
                "character": draw(_ASCII_TEXT),
                "order": i,
            }
        )

    has_director = draw(st.booleans())
    crew: list[dict] = []
    if has_director:
        crew.append(
            {
                "id": 99_999,
                "name": draw(_ASCII_NAME),
                "job": "Director",
            }
        )
    # Thêm vài crew member khác (không phải director) để xác nhận
    # _find_director không nhặt nhầm.
    extra_crew_count = draw(st.integers(min_value=0, max_value=3))
    for j in range(extra_crew_count):
        crew.append(
            {
                "id": 80_000 + j,
                "name": f"Crew {j}",
                "job": draw(
                    st.sampled_from(["Producer", "Writer", "Editor", "Composer"])
                ),
            }
        )

    return {
        "id": draw(st.integers(min_value=1, max_value=10**6)),
        "title": title,
        "release_date": f"{year:04d}-01-01",
        "_year": year,  # giữ riêng để build expected pattern không phụ thuộc parsing
        "genres": [
            {"id": idx, "name": name} for idx, name in enumerate(genre_names)
        ],
        "overview": overview,
        "cast": cast,
        "crew": crew,
        "_has_director": has_director,
        "_cast_size": cast_size,
        "_genre_names": genre_names,
    }


# ---- Property test ----------------------------------------------------------


@given(movie=tmdb_movie_strategy())
@settings(max_examples=100, deadline=None)
def test_chunk_movie_shape(movie: dict) -> None:
    # Feature: ai-chatbot-rag, Property 6: Movie chunking shape. Đúng 1 chunk index 0 với pattern summary; min(k,10) cast top + director; mọi chunk ≤ 512 tokens
    """**Validates: Requirements 3.4**"""

    # Tách meta-fields (prefix ``_``) trước khi đẩy vào chunk_movie để không
    # ảnh hưởng accessor ``_get``.
    expected_year = movie["_year"]
    has_director = movie["_has_director"]
    cast_size = movie["_cast_size"]
    genre_names = movie["_genre_names"]
    payload = {k: v for k, v in movie.items() if not k.startswith("_")}

    chunks = chunk_movie(payload)

    # ---- 1. Đúng 1 chunk có chunk_index == 0 và content khớp pattern --------
    summary_chunks = [c for c in chunks if c["chunk_index"] == 0]
    assert len(summary_chunks) == 1, (
        f"Phải có đúng 1 chunk với chunk_index == 0, có {len(summary_chunks)}"
    )

    summary = summary_chunks[0]
    expected_summary = (
        f"{payload['title']} ({expected_year}) - "
        f"{', '.join(genre_names)}. {payload['overview']}"
    )
    assert summary["content"] == expected_summary, (
        "Chunk 0 không khớp pattern '{title} ({year}) - {genres_csv}. {overview}'"
    )

    # ---- 2. Số chunk còn lại = min(k, 10) cast + (1 nếu có director) -------
    expected_extra = min(cast_size, 10) + (1 if has_director else 0)
    extra_chunks = [c for c in chunks if c["chunk_index"] != 0]
    assert len(extra_chunks) == expected_extra, (
        f"Số cast/director chunk = {len(extra_chunks)}, "
        f"expected {expected_extra} (min({cast_size},10) + "
        f"{1 if has_director else 0})"
    )

    # chunk_index của cast/director phải bắt đầu từ 1 và liên tục.
    actual_indices = sorted(c["chunk_index"] for c in chunks)
    assert actual_indices == list(range(len(chunks))), (
        f"chunk_index phải liên tục 0..n-1, có {actual_indices}"
    )

    # ---- 3. Mọi chunk ≤ 512 tokens (cl100k_base) ---------------------------
    for c in chunks:
        n_tokens = len(_ENCODER.encode(c["content"]))
        assert n_tokens <= 512, (
            f"Chunk {c['chunk_index']} có {n_tokens} tokens > 512: "
            f"{c['content']!r}"
        )


# ---- Edge case sanity (deterministic, không qua Hypothesis) ----------------


def test_chunk_movie_empty_cast_no_director() -> None:
    # Feature: ai-chatbot-rag, Property 6: Movie chunking shape. Đúng 1 chunk index 0 với pattern summary; min(k,10) cast top + director; mọi chunk ≤ 512 tokens
    """**Validates: Requirements 3.4** — k=0, không director ⇒ chỉ có summary."""
    movie = {
        "id": 1,
        "title": "Empty",
        "release_date": "2020-01-01",
        "genres": [],
        "overview": "Nothing.",
        "cast": [],
        "crew": [],
    }
    chunks = chunk_movie(movie)
    assert len(chunks) == 1
    assert chunks[0]["chunk_index"] == 0
    assert chunks[0]["content"] == "Empty (2020) - . Nothing."


def test_chunk_movie_caps_cast_at_ten() -> None:
    # Feature: ai-chatbot-rag, Property 6: Movie chunking shape. Đúng 1 chunk index 0 với pattern summary; min(k,10) cast top + director; mọi chunk ≤ 512 tokens
    """**Validates: Requirements 3.4** — k=15 cast + director ⇒ 1 + 10 + 1 = 12."""
    movie = {
        "id": 2,
        "title": "Big Cast",
        "release_date": "2021-06-01",
        "genres": [{"id": 1, "name": "Drama"}],
        "overview": "Plot.",
        "cast": [
            {"id": i, "name": f"A{i}", "character": f"C{i}"} for i in range(15)
        ],
        "crew": [{"id": 99, "name": "Dir", "job": "Director"}],
    }
    chunks = chunk_movie(movie)
    assert len(chunks) == 1 + 10 + 1
    assert sum(1 for c in chunks if c["metadata"].get("kind") == "cast") == 10
    assert sum(1 for c in chunks if c["metadata"].get("kind") == "director") == 1
