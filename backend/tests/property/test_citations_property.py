# Feature: ai-chatbot-rag, Property 15: Citation round-trip cho mọi danh sách citation hợp lệ và mọi tách rời text không chứa pattern [#...], parse(join(format(c) + t_i)) bằng cs
"""Property-based test cho Citation round-trip.

**Validates: Requirements 10.1, 10.2, 10.3**

Cho danh sách citation hợp lệ ``cs = [Citation(type_i, id_i), ...]`` và danh
sách text fragment ``ts = [t_0, t_1, ..., t_n]`` với ``len(ts) == len(cs) + 1``,
trong đó mọi ``t_i`` không chứa substring ``[#`` (sanitized), property:

    parse(t_0 + format(cs[0]) + t_1 + format(cs[1]) + ... + t_n)
    == [(c.source_type, c.source_id) for c in cs]  # ignore start/end positions
"""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from app.services.ai.citations import (
    SOURCE_TYPES,
    Citation,
    CitationFormatter,
    CitationParser,
)

# ---- Strategies -------------------------------------------------------------


def citation_strategy() -> st.SearchStrategy[Citation]:
    """Sinh Citation hợp lệ: source_type ∈ {"movie","review"}, source_id > 0."""
    return st.builds(
        Citation,
        source_type=st.sampled_from(SOURCE_TYPES),
        # source_id ∈ [1, 10^9] đủ phủ practical range của Postgres bigint.
        source_id=st.integers(min_value=1, max_value=10**9),
    )


def _sanitize_no_citation_marker(s: str) -> str:
    """Loại bỏ mọi xuất hiện của ``[#`` trong ``s``.

    Dùng vòng lặp vì ``str.replace`` chỉ duyệt một lượt nên input
    ``"[[##"`` sẽ còn sót ``"[#"`` sau lần replace đầu. Lặp tới điểm cố định
    đảm bảo invariant ``"[#" not in result``.
    """
    while "[#" in s:
        s = s.replace("[#", "")
    return s


def text_fragment_strategy() -> st.SearchStrategy[str]:
    """Sinh text fragment đã sanitize không chứa ``[#``.

    Cho phép unicode bất kỳ kể cả các ký tự đặc biệt trong grammar
    (``]``, ``:``, digits, ``movie``, ``review``) nhưng cấm marker mở
    ``[#`` để giữ tách rời với citation lân cận.
    """
    return st.text(max_size=30).map(_sanitize_no_citation_marker)


# ---- Property test ----------------------------------------------------------


@given(
    citations=st.lists(citation_strategy(), min_size=0, max_size=20),
    fragments=st.lists(text_fragment_strategy(), min_size=1, max_size=21),
)
@settings(max_examples=200, deadline=None)
def test_citation_round_trip(citations: list[Citation], fragments: list[str]) -> None:
    # Feature: ai-chatbot-rag, Property 15: Citation round-trip
    # Đảm bảo len(fragments) == len(citations) + 1 (tách rời đúng).
    n = len(citations)
    if len(fragments) >= n + 1:
        fragments = fragments[: n + 1]
    else:
        fragments = fragments + [""] * (n + 1 - len(fragments))
    assert len(fragments) == n + 1

    # Build interleaved text: t_0 + format(c_0) + t_1 + ... + t_n
    pieces: list[str] = [fragments[0]]
    for i, c in enumerate(citations):
        pieces.append(CitationFormatter.format(c))
        pieces.append(fragments[i + 1])
    text = "".join(pieces)

    parsed = CitationParser.parse(text)

    expected = [(c.source_type, c.source_id) for c in citations]
    actual = [(p.source_type, p.source_id) for p in parsed]
    assert actual == expected


# ---- Property 16: Parser exception-free on bad input -----------------------

import re

from app.services.ai.citations import CITATION_RE, ParsedCitation


def _bad_bracket_string_strategy() -> st.SearchStrategy[str]:
    """Sinh chuỗi dạng ``[#...]`` *không* khớp grammar.

    Bao gồm các pattern adversarial: thiếu ``:``, source_type lạ
    (``film``, ``rating``, ...), id có leading zero hoặc âm, id chứa ký tự
    không phải số, lồng nhau, v.v.
    """
    inner = st.text(
        alphabet=st.characters(blacklist_characters="]"),
        max_size=20,
    )
    return st.builds(lambda s: f"[#{s}]", inner)


def _adversarial_text_strategy() -> st.SearchStrategy[str]:
    """Sinh text adversarial: unicode tùy ý + đoạn ``[#...]`` đủ kiểu.

    Trộn:
      - text unicode bất kỳ (có thể chứa ``[``, ``#``, ``]`` rời rạc).
      - ``bad_bracket_string`` (dạng ``[#...]`` lệch grammar).
      - citation hợp lệ thật sự (để xác nhận parser vẫn match đúng).
      - một số mẩu ranh giới: ``"[#"``, ``"[#movie:"``, ``"[#movie:0]"``,
        ``"[#review:01]"`` (leading zero), ``"]"``, ``"[#:1]"``.
    """
    valid_citation = st.builds(
        lambda t, i: f"[#{t}:{i}]",
        st.sampled_from(SOURCE_TYPES),
        st.integers(min_value=1, max_value=10**6),
    )
    boundary_pieces = st.sampled_from(
        [
            "[#",
            "[#movie:",
            "[#movie:0]",
            "[#review:01]",
            "[#film:1]",
            "[#:1]",
            "[#movie:abc]",
            "[##movie:1]",
            "[#MOVIE:1]",
            "]",
            "",
        ]
    )
    fragment = st.one_of(
        st.text(max_size=30),
        _bad_bracket_string_strategy(),
        valid_citation,
        boundary_pieces,
    )
    return st.lists(fragment, max_size=12).map("".join)


@given(text=_adversarial_text_strategy())
@settings(max_examples=400, deadline=None)
def test_citation_parser_exception_free_on_arbitrary_unicode(text: str) -> None:
    # Feature: ai-chatbot-rag, Property 16: Parser exception-free trên bad input. Mọi citation trong output đều khớp grammar [#(movie|review):[1-9]\d*]
    """**Validates: Requirements 10.4**

    Với mọi chuỗi unicode bất kỳ (kể cả ``[#...]`` không khớp grammar),
    ``CitationParser.parse`` không raise và mọi ``ParsedCitation`` trả về:

    1. Có ``source_type ∈ {"movie", "review"}``.
    2. Có ``source_id`` là số nguyên dương (không leading zero).
    3. Substring ``text[start:end]`` khớp đúng regex grammar
       ``\\[#(movie|review):[1-9]\\d*\\]``.
    """
    # 1) Không raise cho input str bất kỳ.
    parsed = CitationParser.parse(text)
    assert isinstance(parsed, list)

    grammar_re = re.compile(r"\[#(movie|review):[1-9]\d*\]")
    for p in parsed:
        # 2) Đúng kiểu trả về.
        assert isinstance(p, ParsedCitation)
        # 3) source_type hợp lệ.
        assert p.source_type in SOURCE_TYPES
        # 4) source_id là số nguyên dương thuần (không bool).
        assert isinstance(p.source_id, int) and not isinstance(p.source_id, bool)
        assert p.source_id >= 1
        # 5) Vị trí start/end nằm trong text.
        assert 0 <= p.start < p.end <= len(text)
        # 6) Substring tại vị trí khớp đúng grammar (fullmatch để loại
        #    leading zero và type lạ).
        substring = text[p.start : p.end]
        assert grammar_re.fullmatch(substring), (
            f"Citation substring {substring!r} không khớp grammar"
        )
        # 7) source_type và source_id phải tương ứng với substring.
        m = CITATION_RE.fullmatch(substring)
        assert m is not None
        assert m.group("type") == p.source_type
        assert int(m.group("id")) == p.source_id


# Edge cases: parse phải xử lý được ngay cả input rỗng / không phải citation.
def test_citation_parser_empty_and_non_citation_inputs() -> None:
    # Feature: ai-chatbot-rag, Property 16: Parser exception-free trên bad input. Mọi citation trong output đều khớp grammar [#(movie|review):[1-9]\d*]
    """**Validates: Requirements 10.4**

    Sanity check cho một số input cụ thể:
    - Chuỗi rỗng → ``[]``.
    - ``[#...]`` không khớp grammar → bỏ qua, không raise.
    - Hỗn hợp citation hợp lệ + bad bracket → chỉ trả về citation hợp lệ.
    """
    assert CitationParser.parse("") == []

    bad_inputs = [
        "[#movie:0]",  # leading-zero id (id phải > 0, không bắt đầu '0')
        "[#review:01]",  # leading zero
        "[#movie:-1]",  # âm
        "[#movie:abc]",  # id không phải số
        "[#film:1]",  # source_type lạ
        "[#MOVIE:1]",  # case-sensitive grammar
        "[#movie 1]",  # thiếu ':'
        "[#:1]",  # thiếu source_type
        "##movie:1##",  # khác delimiter
        "[#movie:1",  # thiếu ']'
        "movie:1]",  # thiếu '[#'
    ]
    for s in bad_inputs:
        assert CitationParser.parse(s) == [], (
            f"Bad input {s!r} không nên match nhưng lại match"
        )

    mixed = "abc [#movie:0] xyz [#movie:42] qrs [#film:7] [#review:9]"
    parsed = CitationParser.parse(mixed)
    assert [(p.source_type, p.source_id) for p in parsed] == [
        ("movie", 42),
        ("review", 9),
    ]
