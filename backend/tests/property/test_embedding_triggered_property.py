# Feature: ai-chatbot-rag, Property 29: Embedding triggered cho mọi user message. EmbeddingService.embed gọi đúng 1 lần với content (cache có thể bypass model bên dưới)
"""Property-based test cho Property 29 — stub level (task 6.6).

**Validates: Requirements 4.1**

Theo Requirement 4.1:

    "WHEN Chat_Service nhận một message từ người dùng,
     THE Embedding_Service SHALL sinh vector embedding cho message đó."

Property 29 (xem ``design.md`` mục Properties):

    *For any* user message hợp lệ được gửi qua ``POST /chat/messages``:
    ``EmbeddingService.embed`` được gọi đúng 1 lần với argument bằng
    ``payload.content`` (trừ khi cache hit, trong đó hàm cache vẫn được
    gọi nhưng model bên dưới không).

Task 6.6 ghi chú rõ:

    "Test ở mức Chat_Service mock dùng FakeEmbeddingService counter.
     Có thể hoãn sang task 11 nếu cần Chat_Service; ở đây stub assertion."

Vì Chat_Service chưa tồn tại (task 11), test này stub một "dispatcher"
tối thiểu giả lập điểm gọi ``Embedding_Service.embed`` của Chat_Service:
mọi message đi qua dispatcher phải gọi ``embed`` đúng 1 lần với
``content`` bằng argument. Khi Chat_Service thật được build, task 11.14
sẽ refine test này thay dispatcher stub bằng ``Chat_Service.handle``.

Để giữ scope đúng task 6.6, test KHÔNG ràng buộc backend model bên
dưới — đó là phần ``cache có thể bypass model bên dưới`` của Property 29
và đã được khoá bởi Property 19 (Embedding cache hit/miss trong TTL,
xem ``test_cache_embedding_ttl_property.py``).
"""

from __future__ import annotations

import asyncio

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st


class FakeEmbeddingService:
    """Wrapper counter cho ``EmbeddingService`` — chỉ phục vụ Property 29.

    Khoá invariant tối thiểu mà Chat_Service phải đảm bảo:

    * Mỗi lần ``embed(content)`` được gọi, tăng ``call_count`` và append
      ``content`` vào ``calls`` để test có thể assert đúng giá trị
      argument (Requirement 4.1).
    * Trả về vector deterministic theo ``len(content)`` để dispatcher
      stub không phụ thuộc vào model thật / mạng / cache.

    Lý do dùng wrapper riêng (không tái dùng ``EmbeddingService`` thật):
    Property 29 chỉ quan tâm đến *contract giữa Chat_Service và
    Embedding_Service* — số lần gọi và argument — chứ không quan tâm
    cache hay model. Wrapper counter là cách rõ ràng và rẻ nhất.
    """

    DIMENSION: int = 4

    def __init__(self) -> None:
        self.call_count: int = 0
        self.calls: list[str] = []

    async def embed(self, content: str) -> list[float]:
        self.call_count += 1
        self.calls.append(content)
        # Vector giả deterministic; nội dung không quan trọng cho Property 29.
        base = float(len(content))
        return [base + float(i) for i in range(self.DIMENSION)]


async def _stub_chat_dispatch(
    service: FakeEmbeddingService, content: str
) -> list[float]:
    """Stub cho ``Chat_Service.handle_user_message`` ở mức Property 29.

    Mô phỏng đúng hành vi mà Chat_Service phải có theo Requirement 4.1:
    "khi nhận một user message, Embedding_Service SHALL sinh vector
    embedding cho message đó". Stub gọi ``service.embed(content)`` đúng
    một lần và trả vector.

    Khi Chat_Service thật được hoàn thiện ở task 11, task 11.14 sẽ thay
    stub này bằng pipeline ``Chat_Service.handle(payload)`` thật.
    """
    return await service.embed(content)


# ---- Strategies -------------------------------------------------------------


def _user_message_strategy() -> st.SearchStrategy[str]:
    """Sinh nội dung message tuỳ ý.

    Property 29 nói "mọi user message hợp lệ". Ở mức stub này, ta không
    áp validation length/whitespace (đó là Property 31, ràng buộc bởi
    Requirements 12.1, 12.2 — sẽ được test riêng). Cho phép unicode bất
    kỳ kể cả rỗng để bắt regression nếu code path "skip embed cho
    content rỗng" được thêm vào ngầm.

    ``max_size=200`` đủ phủ practical user message (giới hạn nghiệp vụ
    là 2000 ký tự) mà vẫn nhanh cho hypothesis.
    """
    return st.text(min_size=0, max_size=200)


# ---- Property test ----------------------------------------------------------


@given(content=_user_message_strategy())
@settings(
    max_examples=200,
    deadline=None,
    # Mỗi example dùng FakeEmbeddingService riêng, không có shared
    # state giữa các lần generate; vẫn suppress để hypothesis không
    # cảnh báo về function-scoped fixture pattern (đồng nhất với các
    # property test khác trong repo).
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
def test_embedding_triggered_exactly_once_with_content(content: str) -> None:
    # Feature: ai-chatbot-rag, Property 29: Embedding triggered cho mọi user message. EmbeddingService.embed gọi đúng 1 lần với content (cache có thể bypass model bên dưới)
    """**Validates: Requirements 4.1**

    Với mọi ``content`` hợp lệ, sau khi dispatcher xử lý đúng một message:

    1. ``service.call_count == 1`` — embed được gọi đúng một lần.
    2. ``service.calls == [content]`` — argument bằng ``content`` truyền
       vào (cùng giá trị, không bị normalize / strip / cắt).
    """
    service = FakeEmbeddingService()

    asyncio.run(_stub_chat_dispatch(service, content))

    assert service.call_count == 1, (
        "Property 29 vi phạm: embed phải được gọi đúng 1 lần cho mỗi "
        f"user message, nhận {service.call_count} lần."
    )
    assert service.calls == [content], (
        "Property 29 vi phạm: argument của embed phải bằng content gốc, "
        f"nhận {service.calls!r} thay vì [{content!r}]."
    )


# ---- Sanity check (concrete example) ---------------------------------------


def test_embedding_triggered_concrete_example() -> None:
    # Feature: ai-chatbot-rag, Property 29: Embedding triggered cho mọi user message. EmbeddingService.embed gọi đúng 1 lần với content (cache có thể bypass model bên dưới)
    """**Validates: Requirements 4.1**

    Sanity: gửi một message tiếng Việt cụ thể, embed được gọi đúng 1
    lần với argument đúng.
    """
    service = FakeEmbeddingService()
    content = "phim hành động Hàn Quốc có yếu tố trinh thám"

    vector = asyncio.run(_stub_chat_dispatch(service, content))

    assert service.call_count == 1
    assert service.calls == [content]
    # Vector trả về từ FakeEmbeddingService có dimension đúng.
    assert len(vector) == FakeEmbeddingService.DIMENSION
