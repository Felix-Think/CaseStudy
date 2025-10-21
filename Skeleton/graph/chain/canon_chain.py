from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, ConfigDict, Field

load_dotenv()


class PersonaPresence(BaseModel):
    """Single persona scheduled for a phase."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    persona_id: str = Field(..., description="ID persona (ví dụ P1).")
    role: Optional[str] = Field(
        default=None,
        description="Vai trò hoặc mô tả rất ngắn (nếu cần).",
    )


class CanonEvent(BaseModel):
    """Single canonical event that drives the scenario."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    id: str = Field(..., description="Mã sự kiện duy nhất, ví dụ CE1.")
    title: str
    description: str
    preconditions: List[str]
    success_criteria: List[str]
    timeout_turn: int = Field(
        ...,
        ge=1,
        description="Số lượt hội thoại tối đa trước khi xem là thất bại.",
    )
    npc_appearance: List[PersonaPresence] = Field(
        default_factory=list,
        description="Danh sách persona xuất hiện trong sự kiện.",
    )
    on_success: str | None = Field(
        default=None,
        description="ID sự kiện tiếp theo khi thành công (hoặc null nếu kết thúc).",
    )
    on_fail: str = Field(
        ...,
        description="ID sự kiện fallback khi thất bại (mặc định CE#_RETRY).",
    )


class SkeletonPlan(BaseModel):
    """Full skeleton generation output."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    case_id: str = Field(..., alias="case_id")
    canon_events: List[CanonEvent] = Field(default_factory=list, alias="canon_events")


_parser = PydanticOutputParser(pydantic_object=SkeletonPlan)


def _format_objectives(objs: List[Dict[str, Any]]) -> str:
    lines: List[str] = []
    for item in objs:
        title = item.get("title", "")
        description = item.get("description", "")
        success = item.get("success_criteria", [])
        parts: List[str] = []
        if title:
            parts.append(f"Tiêu đề: {title}")
        if description:
            parts.append(f"Mô tả: {description}")
        if success:
            joined = "; ".join(str(s) for s in success)
            parts.append(f"Tiêu chí thành công: {joined}")
        if parts:
            lines.append(" - " + " | ".join(parts))
    return "\n".join(lines) if lines else "(không có)"


def _format_personas(personas: List[Dict[str, Any]]) -> str:
    blocks: List[str] = []
    for persona in personas:
        role = persona.get("role", "")
        name = persona.get("name", "")
        persona_id = persona.get("id") or persona.get("persona_id") or ""
        snippet = []
        if persona_id:
            snippet.append(f"ID: {persona_id}")
        snippet.append(f"Vai trò: {role}")
        if name:
            snippet.append(f"Tên: {name}")
        blocks.append(" | ".join(snippet))
    return "\n".join(blocks) if blocks else "(không có)"


_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Bạn là chuyên gia thiết kế tình huống huấn luyện nhập vai. "
            "Dựa trên thông tin case study, hãy xây dựng danh sách canon events theo đúng format JSON. "
            "Tuân thủ chính xác schema sau: {format_instructions}. "
            "Tất cả nội dung phải dùng tiếng Việt chuyên nghiệp, súc tích, tránh lặp từ.",
        ),
        (
            "human",
            "CASE ID: {case_id}\n"
            "Chủ đề: {topic}\n"
            "Ngôn ngữ: {language}\n\n"
            "Tóm tắt bối cảnh:\n{context_summary}\n\n"
            "Mục tiêu học tập:\n{objectives_text}\n\n"
            "Personas liên quan:\n{personas_text}\n\n"
            "YÊU CẦU:\n"
            "- Sinh tối thiểu canon events để bao phủ các mục tiêu học tập đã nêu, mỗi event bám sát một mục tiêu tương ứng.\n"
            "- Mỗi event phải mô tả nhiệm vụ, hành động bắt buộc để thoả mãn Learning Objective rõ ràng.\n"
            "- Trường on_success dùng ID sự kiện tiếp theo hoặc null nếu kết thúc.\n"
            "- Trường on_fail bắt buộc dùng ID retry theo mẫu <ID>_RETRY (ví dụ CE2_RETRY).\n"
            "- Trường timeout_turn là số lượt hội thoại tối đa trước khi event xem như thất bại (số nguyên >= 1).\n"
            "- Trường preconditions là danh sách ID sự kiện cần hoàn thành trước (có thể rỗng).\n"
            "- Trong mỗi canon event, trường npc_appearance là danh sách personas xuất hiện (persona_id khớp dữ liệu đầu vào, kèm role).\n"
            "- Không cần đảm bảo tất cả personas đều xuất hiện trong mỗi npc_appearance.\n"
            "- Không thêm trường ngoài schema quy định.\n",
        ),
    ]
).partial(format_instructions=_parser.get_format_instructions())

_llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.4,
    api_key=os.getenv("OPENAI_API_KEY"),
)


def build_canon_plan(
    *,
    case_id: str,
    topic: str,
    language: str,
    objectives: List[Dict[str, Any]],
    personas: List[Dict[str, Any]],
    context_summary: str,
) -> Dict[str, Any]:
    """Generate canon events + outline from structured case inputs."""
    objectives_text = _format_objectives(objectives)
    personas_text = _format_personas(personas)

    chain = _prompt | _llm | _parser
    result = chain.invoke(
        {
            "case_id": case_id or "unknown_case",
            "topic": topic or "(không rõ)",
            "language": language or "vi-VN",
            "objectives_text": objectives_text,
            "personas_text": personas_text,
            "context_summary": context_summary,
        }
    )
    return result.model_dump()
