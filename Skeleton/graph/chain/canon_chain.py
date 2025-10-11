from __future__ import annotations

import os
from typing import Any, Dict, List

from dotenv import load_dotenv
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, ConfigDict, Field

load_dotenv()


class CanonEvent(BaseModel):
    """Single canonical event that drives the scenario."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    id: str = Field(..., description="Mã sự kiện duy nhất, viết hoa và dùng dấu gạch dưới.")
    title: str
    description: str
    trigger: str
    preconditions: List[str]
    required_actions: List[str]
    success_criteria: List[str]
    phase_id: str = Field(..., alias="phase_id", description="ID phase chứa sự kiện.")
    timeout_turn: int = Field(..., alias="timeout_turn", ge=1, description="Số lượt hội thoại tối đa.")
    npc_lines: List[str] = Field(default_factory=list, description="Các câu thoại mẫu của NPC (nếu có).")
    fail_risk: str
    on_success: List[str] = Field(default_factory=list)
    on_fail: List[str] = Field(default_factory=list)


class SkeletonPlan(BaseModel):
    """Full skeleton generation output."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    case_id: str = Field(..., alias="case_id")
    canon_events: List[CanonEvent] = Field(default_factory=list, alias="canon_events")
    telemetry: Dict[str, Any] = Field(default_factory=dict, alias="telemetry")


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
        traits = persona.get("traits") or persona.get("notes_for_dialogue") or []
        goals = persona.get("goals", [])
        snippet = [f"Vai trò: {role}"]
        if name:
            snippet.append(f"Tên: {name}")
        if goals:
            snippet.append("Mục tiêu: " + "; ".join(goals))
        if traits:
            snippet.append("Đặc điểm: " + "; ".join(str(t) for t in traits))
        blocks.append(" | ".join(snippet))
    return "\n".join(blocks) if blocks else "(không có)"


_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Bạn là chuyên gia thiết kế tình huống huấn luyện nhập vai. "
            "Dựa trên thông tin case study, hãy xây dựng danh sách canon events chi tiết gắn với mục tiêu học tập "
            "và đề xuất telemetry tổng quan cho toàn kịch bản. "
            "Tuân thủ chặt schema JSON đã cho: {format_instructions}. "
            "Luôn viết tiếng Việt chuyên nghiệp, súc tích, không lặp từ."
        ),
        (
            "human",
            "case_id: {case_id}\n"
            "Chủ đề: {topic}\n"
            "Mục tiêu học tập:\n{objectives_text}\n\n"
            "Bối cảnh chính: {context_summary}\n"
            "Nhân vật quan trọng:\n{personas_text}\n"
            "Ngôn ngữ hiển thị: {language}\n\n"
            "Yêu cầu chi tiết:\n"
            "- canon_events gồm 7-10 mục, id dạng CE#_TÊN_VIẾT_HOA, mô tả hành động cụ thể, nêu rõ trigger và chỉ dẫn theo turn.\n"
            "- Mỗi sự kiện phải có: phase_id (chỉ định nhịp câu chuyện), trigger cụ thể, preconditions, required_actions ≥3 hành động rõ ràng, success_criteria ≥2, timeout_turn ≥2.\n"
            "- Nếu liên quan persona, thêm 'npc_lines' với ≥2 câu thoại mẫu phù hợp.\n"
            "- on_success/on_fail: chỉ chứa id sự kiện kế tiếp; mảng rỗng nếu kết thúc một nhánh.\n"
            "- telemetry: log_events true/false, metrics là danh sách chỉ số cấp kịch bản (dùng định dạng '<phase_id>.<metric>'), phase_rollup liệt kê mỗi phase với metrics và targets tương ứng.\n"
            "Chỉ trả về JSON hợp lệ."
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
