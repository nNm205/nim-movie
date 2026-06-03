"""Unit test cho ``app.schemas.chat.ChatMessageCreate``.

**Validates: Requirements 12.1, 12.2**

Các trường hợp được cover (theo task 4.2):

- Reject ``len(content) > 2000`` → Pydantic ``ValidationError``
  (Requirement 12.1: Chat_Service từ chối message > 2000 ký tự).
- Reject content rỗng / chỉ chứa whitespace: ``""``, ``"   "``, ``"\t\n"``,
  và full-width space ``"\u3000"``
  (Requirement 12.2: loại bỏ message rỗng hoặc chỉ chứa khoảng trắng).
- Accept content 1 ký tự (biên dưới hợp lệ).
- Accept content 2000 ký tự (biên trên hợp lệ).
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.schemas.chat import ChatMessageCreate


# ---------------------------------------------------------------------------
# Reject: oversize content (Requirement 12.1)
# ---------------------------------------------------------------------------
class TestChatMessageCreateRejectOversize:
    """Content > 2000 ký tự phải bị từ chối với ``ValidationError``."""

    def test_reject_2001_chars(self) -> None:
        oversize = "a" * 2001
        with pytest.raises(ValidationError) as exc_info:
            ChatMessageCreate(content=oversize)
        # Pydantic v2 attaches loc=("content",) cho field-level lỗi.
        errors = exc_info.value.errors()
        assert any(err["loc"] == ("content",) for err in errors)

    def test_reject_far_oversize(self) -> None:
        # Cận xa khỏi giới hạn: vẫn phải reject.
        with pytest.raises(ValidationError):
            ChatMessageCreate(content="x" * 5000)


# ---------------------------------------------------------------------------
# Reject: empty / whitespace-only content (Requirement 12.2)
# ---------------------------------------------------------------------------
class TestChatMessageCreateRejectWhitespaceOnly:
    """``""`` bị reject bởi ``min_length=1``; các whitespace khác bởi validator."""

    @pytest.mark.parametrize(
        "value",
        [
            "",          # rỗng tuyệt đối
            "   ",       # ASCII space
            "\t\n",      # tab + newline
            "\u3000",    # full-width space (U+3000)
            "\u3000\u3000",  # nhiều full-width space liên tiếp
            " \t\n\u3000 ",  # hỗn hợp ASCII + full-width whitespace
        ],
    )
    def test_reject_whitespace_only(self, value: str) -> None:
        with pytest.raises(ValidationError) as exc_info:
            ChatMessageCreate(content=value)
        errors = exc_info.value.errors()
        assert any(err["loc"] == ("content",) for err in errors)


# ---------------------------------------------------------------------------
# Accept: boundary lengths (Requirement 12.1)
# ---------------------------------------------------------------------------
class TestChatMessageCreateAcceptBoundaries:
    """Content có độ dài hợp lệ 1..2000 phải được accept y nguyên."""

    def test_accept_single_char(self) -> None:
        m = ChatMessageCreate(content="a")
        assert m.content == "a"
        assert m.session_id is None

    def test_accept_2000_chars(self) -> None:
        content = "b" * 2000
        m = ChatMessageCreate(content=content)
        assert m.content == content
        assert len(m.content) == 2000

    def test_accept_content_with_surrounding_whitespace(self) -> None:
        # Có ký tự thực sau strip → vẫn hợp lệ; validator không trim giá trị,
        # chỉ kiểm tra non-empty sau strip.
        raw = "  hello  "
        m = ChatMessageCreate(content=raw)
        assert m.content == raw
