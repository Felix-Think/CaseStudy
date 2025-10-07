import json
from typing import Any, Dict, Iterable, List

from dotenv import load_dotenv
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from agent.state import GraphState

load_dotenv()


class SceneNarration(BaseModel):
    scene_narration: str = Field(
        ...,
        description="Đoạn dẫn chuyện bằng tiếng Việt, mô tả bối cảnh hiện tại và cảm giác nhập vai.",
    )
    narrator_focus: str = Field(
        ...,
        description="Một câu ngắn gợi ý hướng dẫn tiếp theo mà người học nên chú ý.",
    )
    narrative_mode: str = Field(
        ...,
        description="with_persona nếu đang tương tác thông qua nhân vật phụ; narrator_only nếu không có nhân vật phụ.",
    )


def _ensure_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, dict):
        cleaned = {k: v for k, v in value.items() if v not in (None, "", [], {})}
        return json.dumps(cleaned, ensure_ascii=False)
    if isinstance(value, list):
        parts = []
        for item in value:
            if isinstance(item, dict):
                parts.append(json.dumps(item, ensure_ascii=False))
            else:
                parts.append(str(item))
        return ", ".join(part for part in parts if part)
    return str(value)


def _format_entry(entry: Dict[str, Any]) -> str:
    if not entry:
        return ""
    parts: List[str] = []
    dialogue = entry.get("dialogue")
    if dialogue:
        parts.append(f'Lời nói: "{dialogue}"')
    action = entry.get("action")
    if action:
        parts.append(f"Hành động: {action}")
    emotion = entry.get("emotion")
    if emotion:
        parts.append(f"Cảm xúc: {emotion}")
    context = entry.get("context")
    if context:
        parts.append(f"Ngữ cảnh: {context}")
    return "; ".join(parts)


def _format_history(entries: Iterable[Dict[str, Any]], limit: int = 4) -> str:
    subset = list(entries)[-limit:]
    if not subset:
        return ""
    lines: List[str] = []
    for item in subset:
        speaker = item.get("speaker", "")
        summary = _format_entry(item)
        if summary:
            lines.append(f"{speaker}: {summary}")
    return " | ".join(lines)


parser = PydanticOutputParser(pydantic_object=SceneNarration)

scene_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Bạn là người dẫn chuyện trong huấn luyện nhập vai. "
            "Luôn viết bằng tiếng Việt sinh động, ngôi thứ hai. "
            "Nếu narrative_mode là 'with_persona', hãy mô tả tương tác giữa người học và nhân vật phụ hiện tại, "
            "đưa nhân vật phụ vào cảnh theo trạng thái mới nhất của họ. "
            "Hãy xem xét trạng thái, cảm xúc và mục tiêu của nhân vật phụ để tạo ra các tương tác phù hợp. "
            "Nếu narrative_mode là 'narrator_only', người dẫn chuyện thay nhân vật phụ tiếp cận trực tiếp nhân vật chính. "
            "Nếu story_phase là 'opening' hãy mở đầu bối cảnh gợi mở; nếu là 'continuation', nối tiếp trực tiếp từ hành động/cảm xúc gần nhất. "
            "Giữ độ dài dưới 160 chữ. Không giải quyết xung đột. Trả về JSON theo schema: {format_instructions}."
            "Trường narrative_mode trong JSON phải khớp chính xác giá trị được cung cấp." 
        ),
        (
            "human",
            "Tên kịch bản: {scenario_name}\n"
            "Mục tiêu học tập: {learning_objective}\n"
            "Bối cảnh ban đầu: {initial_context_text}\n"
            "Hồ sơ nhân vật phụ: {persona_profile}\n"
            "Tóm tắt lượt nhân vật phụ gần nhất: {persona_snapshot}\n"
            "Lịch sử nhân vật phụ: {persona_history}\n"
            "Tóm tắt lượt nhân vật chính gần nhất: {main_snapshot}\n"
            "Lịch sử nhân vật chính: {main_history}\n"
            "Ghi chú thêm: {narration_notes}\n"
            "Pha câu chuyện: {story_phase}\n"
            "Chế độ tương tác: {narrative_mode}"
        ),
    ]
).partial(format_instructions=parser.get_format_instructions())


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.6)


def build_scene_narration(state: GraphState) -> Dict[str, str]:
    scenario_name = state.get("Scenario_Name", "")
    learning_objective = _ensure_text(state.get("Learning_Objective", {}))
    initial_context_text = _ensure_text(state.get("Initial_Context", {}))

    persona_profile = _ensure_text(state.get("Persona", {}))
    persona_entry = state.get("Persona_Current", {}) or {}
    persona_snapshot = _format_entry(persona_entry)
    persona_history = _format_history(state.get("Persona_Dialogue_Log", []) or [])

    main_entry = state.get("Main_Current", {}) or {}
    main_snapshot = _format_entry(main_entry)
    main_history = _format_history(state.get("Main_Dialogue_Log", []) or [])

    narration_notes = _ensure_text(state.get("Narration_Notes", ""))

    persona_present = bool(persona_snapshot or persona_history or persona_profile)
    narrative_mode = "with_persona" if persona_present else "narrator_only"

    story_phase = "opening"
    if main_snapshot or main_history or persona_history:
        story_phase = "continuation"

    chain = scene_prompt | llm | parser
    result = chain.invoke(
        {
            "scenario_name": scenario_name,
            "learning_objective": learning_objective,
            "initial_context_text": initial_context_text,
            "persona_profile": persona_profile or "(không có nhân vật phụ)",
            "persona_snapshot": persona_snapshot or "(chưa phát biểu)",
            "persona_history": persona_history or "(chưa có lịch sử)",
            "main_snapshot": main_snapshot or "(chưa có phản hồi của nhân vật chính)",
            "main_history": main_history or "(chưa có lịch sử)",
            "narration_notes": narration_notes or "",
            "story_phase": story_phase,
            "narrative_mode": narrative_mode,
        }
    )

    narrative_mode_out = result.narrative_mode or narrative_mode

    return {
        "Scene_Narration": result.scene_narration,
        "Narrator_Focus": result.narrator_focus,
        "Story_Phase": story_phase,
        "Narrative_Mode": narrative_mode_out,
        "Persona_Present": persona_present,
    }
