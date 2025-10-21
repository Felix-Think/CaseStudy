from __future__ import annotations

import os
from typing import Any, Dict, List

from dotenv import load_dotenv
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, ConfigDict, Field

load_dotenv()


class PersonaProfile(BaseModel):
    """Structured persona profile output."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    id: str = Field(..., description="ID duy nhất, ví dụ P1.")
    name: str = Field(..., description="Tên hiển thị hoặc mô tả ngắn.")
    role: str = Field(..., description="Vai trò trong kịch bản.")
    age: int = Field(..., ge=0, description="Tuổi ước tính (số nguyên).")
    gender: str = Field(..., description="Giới tính thể hiện cách xưng hô.")
    background: str = Field(..., description="Bối cảnh cá nhân liên quan.")
    personality: str = Field(..., description="Đặc điểm tính cách nổi bật.")
    goal: str = Field(..., description="Mục tiêu chính của persona.")
    speech_pattern: str = Field(..., description="Phong cách lời thoại.")
    emotion_init: str = Field(..., description="Cảm xúc mở đầu.")
    emotion_during: List[str] = Field(
        default_factory=list,
        description="Chuỗi cảm xúc có thể xảy ra trong tương tác.",
    )
    emotion_end: str = Field(..., description="Cảm xúc kết thúc kỳ vọng.")
    voice_tags: List[str] = Field(
        default_factory=list,
        description="Thẻ giọng nói để gợi ý synthetic voice.",
    )


class PersonaPlan(BaseModel):
    """Container for persona plan."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    case_id: str = Field(..., description="ID case study.")
    personas: List[PersonaProfile] = Field(
        default_factory=list, description="Danh sách persona."
    )


_parser = PydanticOutputParser(pydantic_object=PersonaPlan)


def _summarize_context(context: Dict[str, Any]) -> str:
    if not context:
        return "(không có thông tin bối cảnh)"

    blocks: List[str] = []

    scene = context.get("scene") or {}
    if scene:
        descriptors = []
        time = scene.get("time")
        location = scene.get("location")
        weather = scene.get("weather")
        noise = scene.get("noise_level")
        if time:
            descriptors.append(f"Thời gian: {time}")
        if location:
            descriptors.append(f"Địa điểm: {location}")
        if weather:
            descriptors.append(f"Thời tiết: {weather}")
        if noise:
            descriptors.append(f"Độ ồn: {noise}")
        if descriptors:
            blocks.append("Cảnh: " + "; ".join(descriptors))

    index_event = context.get("index_event") or {}
    if index_event:
        summary = index_event.get("summary")
        state = index_event.get("current_state")
        who_first = index_event.get("who_first_on_scene")
        if summary:
            blocks.append(f"Tình huống: {summary}")
        if state:
            blocks.append(f"Tình trạng hiện tại: {state}")
        if who_first:
            blocks.append(f"Người đầu tiên tiếp cận: {who_first}")

    constraints = context.get("constraints") or []
    if constraints:
        joined = "; ".join(str(item) for item in constraints)
        blocks.append(f"Hạn chế: {joined}")

    resources = context.get("available_resources") or {}
    if resources:
        details = []
        for label, items in resources.items():
            if items:
                joined = ", ".join(str(item) for item in items)
                details.append(f"{label}: {joined}")
        if details:
            blocks.append("Nguồn lực: " + " | ".join(details))

    policies = context.get("policies_safety_legal") or []
    if policies:
        blocks.append(
            "Chính sách/An toàn: " + "; ".join(str(policy) for policy in policies)
        )

    handover = context.get("handover_target")
    if handover:
        blocks.append(f"Mục tiêu bàn giao: {handover}")

    return "\n".join(blocks) if blocks else "(không có thông tin bối cảnh)"


def _format_source_personas(personas: List[Dict[str, Any]]) -> str:
    if not personas:
        return "(không cung cấp sẵn persona)"

    rows: List[str] = []
    for persona in personas:
        pid = persona.get("id") or ""
        name = persona.get("name") or ""
        role = persona.get("role") or ""
        traits = persona.get("traits") or persona.get("attributes") or []
        state = persona.get("state")
        parts: List[str] = []
        if name:
            parts.append(f"Tên: {name}")
        if role:
            parts.append(f"Vai trò: {role}")
        if state:
            parts.append(f"Tình trạng: {state}")
        if traits:
            trait_text = ", ".join(str(t) for t in traits)
            parts.append(f"Đặc điểm: {trait_text}")
        rows.append(f"{pid}: " + " | ".join(parts) if parts else pid)
    return "\n".join(rows)


_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Bạn là chuyên gia thiết kế persona cho mô phỏng y khoa. "
            "Hãy xây dựng JSON personas theo đúng schema cung cấp. "
            "Nội dung phải chuyên nghiệp, cô đọng, ưu tiên tiếng Việt cho mô tả nhưng voice_tags dùng tiếng Anh đơn giản.",
        ),
        (
            "human",
            "CASE ID: {case_id}\n"
            "Chủ đề: {topic}\n"
            "Ngôn ngữ yêu cầu: {language}\n"
            "Ngữ cảnh tổng quát:\n{context_summary}\n\n"
            "Dữ liệu persona ban đầu:\n{source_personas}\n\n"
            "YÊU CẦU:\n"
            "- Tuân thủ chính xác schema JSON: {format_instructions}.\n"
            "- Gán tuổi phù hợp với vai trò (số nguyên).\n"
            "- Mô tả tính cách, mục tiêu và cách nói ngắn gọn, dễ hiểu.\n"
            "- Chuỗi emotion_during phải phản ánh diễn biến cảm xúc hợp lý.\n"
            "- voice_tags là danh sách các nhãn tiếng Việt dạng snake_case, 1-3 mục.\n"
            "- Không thêm trường ngoài schema. Không để trống trường bắt buộc.\n"
            "- Nếu thiếu thông tin đầu vào, suy luận hợp lý nhưng giữ nhất quán với bối cảnh.",
        ),
    ]
).partial(format_instructions=_parser.get_format_instructions())

_llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.4,
    api_key=os.getenv("OPENAI_API_KEY"),
)


def build_persona_plan(
    *,
    case_id: str,
    topic: str,
    language: str,
    context: Dict[str, Any],
    personas: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Generate enriched persona profiles from structured case inputs."""
    context_summary = _summarize_context(context)
    source_personas = _format_source_personas(personas)

    chain = _prompt | _llm | _parser
    result = chain.invoke(
        {
            "case_id": case_id or "unknown_case",
            "topic": topic or "(không rõ)",
            "language": language or "vi-VN",
            "context_summary": context_summary,
            "source_personas": source_personas,
        }
    )
    return result.model_dump()
