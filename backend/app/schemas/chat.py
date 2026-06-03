"""
Pydantic v2 schemas cho Chat_API (Requirements 1.1, 1.5, 1.6, 12.1, 12.2).

Các schema được nhóm theo:
- Inbound (request body): ChatMessageCreate, ReindexRequest.
- Citation primitive (shared): CitationOut.
- Outbound đơn lẻ: ChatMessageOut, ChatSessionOut, ChatMessageResponse,
  ReindexResponse, ChatbotStatsResponse.
- Outbound list: ChatSessionListResponse, ChatMessageListResponse.

Convention:
- Dùng Pydantic v2 (`model_config = ConfigDict(from_attributes=True)`) cho các
  schema được build từ ORM (ChatSession, ChatMessage).
- Type hint Literal cho `role` và `source_type` để FastAPI sinh OpenAPI enum
  và để mypy bắt được lỗi gán giá trị ngoài tập hợp.
- ChatMessageCreate.content có cả `min_length=1, max_length=2000` (Requirement
  12.1) và validator strip whitespace để chống message chỉ chứa khoảng trắng,
  bao gồm cả full-width space (U+3000) và whitespace Unicode khác — `str.strip()`
  trong Python 3 mặc định xử lý theo Unicode whitespace.
"""

from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

# Tập hợp role và source_type được phơi ra như Literal để các module khác
# (ví dụ Chat_Service, Citation_Codec) có thể import lại cùng một định nghĩa.
RoleLiteral = Literal["user", "assistant", "system"]
SourceTypeLiteral = Literal["movie", "review"]
ReindexSourceLiteral = Literal["movie", "review", "all"]


# ---------------------------------------------------------------------------
# Inbound: POST /chat/messages
# ---------------------------------------------------------------------------
class ChatMessageCreate(BaseModel):
    """
    Body cho POST /api/v1/chat/messages.

    - `session_id` None → Chat_Service tạo session mới (Requirement 1.1).
    - `content` 1..2000 ký tự (Requirement 12.1) và không được chỉ là whitespace
      (Requirement 12.2). Validator dùng `str.strip()` để bắt cả full-width
      space và whitespace Unicode khác. Khi không hợp lệ raise `ValueError`,
      FastAPI sẽ render thành HTTP 422.
    """

    session_id: Optional[UUID] = None
    content: str = Field(min_length=1, max_length=2000)

    @field_validator("content")
    @classmethod
    def _reject_whitespace_only(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Message cannot be empty or whitespace-only")
        return value


# ---------------------------------------------------------------------------
# Citation
# ---------------------------------------------------------------------------
class CitationOut(BaseModel):
    """
    Citation được trả về kèm assistant message.

    Khớp grammar `[#{source_type}:{source_id}]` (Requirement 10.1):
    - `source_type` thuộc {"movie", "review"}.
    - `source_id` là số nguyên dương.
    """

    source_type: SourceTypeLiteral
    source_id: int = Field(ge=1)


# ---------------------------------------------------------------------------
# Outbound: ChatMessage / ChatSession
# ---------------------------------------------------------------------------
class ChatMessageOut(BaseModel):
    """
    Một message trong response GET /chat/sessions/{id}/messages.

    `from_attributes=True` cho phép build từ ORM `ChatMessage` (Requirement 1.6).
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: UUID
    role: RoleLiteral
    content: str
    citations: Optional[list[CitationOut]] = None
    tokens_input: Optional[int] = None
    tokens_output: Optional[int] = None
    created_at: datetime


class ChatSessionOut(BaseModel):
    """
    Một session trong response GET /chat/sessions (Requirement 1.5).
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: int
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Outbound: list responses
# ---------------------------------------------------------------------------
class ChatSessionListResponse(BaseModel):
    """
    Response cho GET /chat/sessions (Requirement 1.5).
    Mặc định page_size = 20, sort theo updated_at DESC do service xử lý.
    """

    items: list[ChatSessionOut]
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    total: int = Field(ge=0)


class ChatMessageListResponse(BaseModel):
    """
    Response cho GET /chat/sessions/{session_id}/messages (Requirement 1.6).
    Items đã được service sort theo created_at ASC.
    """

    session_id: UUID
    items: list[ChatMessageOut]


# ---------------------------------------------------------------------------
# Outbound: non-streaming POST /chat/messages
# ---------------------------------------------------------------------------
class ChatMessageResponse(BaseModel):
    """
    Response JSON cho POST /chat/messages khi `Accept` không phải SSE
    (Requirement 5.5). Phân biệt với ChatMessageOut (đại diện một row trong
    list) ở chỗ phía streaming `done` event cũng dùng cấu trúc tương tự.
    """

    message_id: int
    session_id: UUID
    content: str
    citations: list[CitationOut] = Field(default_factory=list)
    tokens_input: Optional[int] = None
    tokens_output: Optional[int] = None


# ---------------------------------------------------------------------------
# Admin reindex
# ---------------------------------------------------------------------------
class ReindexRequest(BaseModel):
    """
    Body cho POST /admin/chatbot/reindex (Requirement 3.8).

    - `source_type` ∈ {"movie","review","all"}.
    - `source_ids` optional; khi None job xử lý theo phạm vi mặc định
      (toàn bộ source thuộc loại đó).
    """

    source_type: ReindexSourceLiteral
    source_ids: Optional[list[int]] = None


class ReindexResponse(BaseModel):
    """
    Response 202 cho POST /admin/chatbot/reindex (Requirement 3.8).
    """

    job_id: UUID


# ---------------------------------------------------------------------------
# Admin stats
# ---------------------------------------------------------------------------
class ChatbotStatsResponse(BaseModel):
    """
    Response cho GET /admin/chatbot/stats (Requirement 13.3).

    - `latency_p50_ms`, `latency_p95_ms` có thể None khi chưa đủ sample
      (in-memory aggregator vừa khởi động).
    - `tokens_by_provider`: ví dụ {"openai": 12345, "groq": 678}.
    """

    total_sessions: int = Field(ge=0)
    messages_last_24h: int = Field(ge=0)
    latency_p50_ms: Optional[float] = None
    latency_p95_ms: Optional[float] = None
    tokens_by_provider: dict[str, int] = Field(default_factory=dict)
