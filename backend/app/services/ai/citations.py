"""Citation codec cho AI Chatbot RAG.

Cung cấp data class cho citation, formatter (render) và parser (extract) theo
grammar `[#<source_type>:<source_id>]` với:

    source_type ∈ {"movie", "review"}
    source_id   ∈ Z>0  (số nguyên dương, không leading zero)

Tham chiếu Requirements: 10.1, 10.2, 10.4 (xem
`.kiro/specs/ai-chatbot-rag/requirements.md`).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Final, Literal

__all__ = [
    "SOURCE_TYPES",
    "CITATION_RE",
    "Citation",
    "ParsedCitation",
    "CitationFormatter",
    "CitationParser",
]

#: Tập hợp source_type hợp lệ cho citation.
SOURCE_TYPES: Final[tuple[str, ...]] = ("movie", "review")

#: Regex grammar cho citation. Chỉ match số nguyên dương không leading zero.
CITATION_RE: Final[re.Pattern[str]] = re.compile(
    r"\[#(?P<type>movie|review):(?P<id>[1-9]\d*)\]"
)


@dataclass(frozen=True)
class Citation:
    """Tham chiếu tới một nguồn trong Knowledge_Base.

    Attributes:
        source_type: Loại nguồn, ``"movie"`` hoặc ``"review"``.
        source_id: ID dương của nguồn trong DB.
    """

    source_type: Literal["movie", "review"]
    source_id: int


@dataclass(frozen=True)
class ParsedCitation(Citation):
    """Citation kèm vị trí xuất hiện trong text gốc.

    Attributes:
        start: Chỉ số bắt đầu (inclusive) trong text gốc.
        end: Chỉ số kết thúc (exclusive) trong text gốc.
    """

    start: int
    end: int


class CitationFormatter:
    """Render Citation thành chuỗi theo grammar ``[#type:id]``."""

    @staticmethod
    def format(c: Citation) -> str:
        """Trả về chuỗi citation đã render.

        Args:
            c: Citation cần render.

        Returns:
            Chuỗi dạng ``"[#movie:123]"`` hoặc ``"[#review:45]"``.

        Raises:
            ValueError: Khi ``source_type`` không thuộc :data:`SOURCE_TYPES`
                hoặc ``source_id`` không phải số nguyên dương.
        """
        if c.source_type not in SOURCE_TYPES:
            raise ValueError(
                f"Invalid source_type {c.source_type!r}; "
                f"expected one of {SOURCE_TYPES!r}"
            )
        # Reject bool (bool is subclass of int) và non-int.
        if not isinstance(c.source_id, int) or isinstance(c.source_id, bool):
            raise ValueError(
                f"Invalid source_id {c.source_id!r}; expected positive int"
            )
        if c.source_id <= 0:
            raise ValueError(
                f"Invalid source_id {c.source_id!r}; must be > 0"
            )
        return f"[#{c.source_type}:{c.source_id}]"


class CitationParser:
    """Extract citation từ một chuỗi text bất kỳ."""

    @staticmethod
    def parse(text: str) -> list[ParsedCitation]:
        """Tìm tất cả citation hợp lệ trong ``text``.

        Match theo :data:`CITATION_RE`. Các chuỗi ``[#...]`` không khớp grammar
        (thiếu ``:``, ``source_type`` lạ, ``source_id`` không phải số dương,
        có leading zero, v.v.) sẽ được bỏ qua. Hàm không bao giờ raise
        exception cho input str hợp lệ (Requirement 10.4).

        Args:
            text: Chuỗi cần parse.

        Returns:
            Danh sách :class:`ParsedCitation` theo thứ tự xuất hiện trong
            ``text``.
        """
        if not text:
            return []
        results: list[ParsedCitation] = []
        for m in CITATION_RE.finditer(text):
            # Regex đã đảm bảo source_type ∈ {"movie","review"} và id là chuỗi
            # số không leading zero. ValueError từ int() không xảy ra.
            source_type = m.group("type")
            source_id = int(m.group("id"))
            results.append(
                ParsedCitation(
                    source_type=source_type,  # type: ignore[arg-type]
                    source_id=source_id,
                    start=m.start(),
                    end=m.end(),
                )
            )
        return results
