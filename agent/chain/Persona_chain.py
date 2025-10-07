"""Persona reaction chain built around dialogue-centric state."""

import json
from typing import Any, Dict, Iterable, List

from dotenv import load_dotenv
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from agent.state import DialogueEntry, GraphState

load_dotenv()


class PersonaReaction(BaseModel):
    persona_dialogue: str = Field(
        ..., description="Lời thoại tiếng Việt của nhân vật phụ ở lượt này (tối đa 2 câu)."
    )
    persona_action: str = Field(
        ..., description="Hành động cụ thể nhân vật phụ thực hiện ngay sau lời thoại."
    )
    persona_emotion: str = Field(
        "", description="Cảm xúc hiện tại của nhân vật phụ sau khi phản hồi."
    )
    persona_context: str = Field(
        "", description="Mô tả ngắn về bối cảnh/cử chỉ đi kèm, nếu cần." 
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
        parts: List[str] = []
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
    pieces: List[str] = []
    dialogue = entry.get("dialogue")
    if dialogue:
        pieces.append(f'Lời nói: "{dialogue}"')
    action = entry.get("action")
    if action:
        pieces.append(f"Hành động: {action}")
    emotion = entry.get("emotion")
    if emotion:
        pieces.append(f"Cảm xúc: {emotion}")
    context = entry.get("context")
    if context:
        pieces.append(f"Ngữ cảnh: {context}")
    return "; ".join(pieces)


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


parser = PydanticOutputParser(pydantic_object=PersonaReaction)

persona_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Bạn nhập vai nhân vật phụ trong một tình huống huấn luyện nhập vai. "
            "Phản hồi bằng tiếng Việt mạch lạc, tối đa 80 chữ cho cả lời nói và mô tả hành động. "
            "Cách nói chuyện ,cảm xúc có thể thay đổi theo ngữ cảnh đặc biệt phải thay đổi cho phù hợp theo hành động của nhân vật chính. "
            "Nếu chế độ tương tác là 'initiate', bạn cần chủ động tiếp cận nhân vật chính. "
            "Nếu chế độ là 'respond', hãy phản hồi trực tiếp dựa trên lời nói/hành động mới nhất của nhân vật chính. Giận dữ, thù địch, hung hăng, bạo lực nếu như cảm xúc hiện tại là như vậy. "
            "Các hành động lời nói không được lặp lại từ những gì đã nói trong lịch sử. "
            "Có thể im lặng nếu cảm thấy không có gì để nói, nếu không thì hãy hành động tùy thuộc vào tính cách hiện tại."
            "Trả về JSON khớp schema: {format_instructions}."
        ),
        (
            "human",
            "Tên kịch bản: {scenario_name}\n"
            "Mục tiêu học tập: {learning_objective}\n"
            "Bối cảnh hiện tại: {scene_narration}\n"
            "Tính cách & thông tin nhân vật phụ: {persona_profile}\n"
            "Lượt gần nhất của nhân vật phụ: {persona_snapshot}\n"
            "Lịch sử nhân vật phụ: {persona_history}\n"
            "Lượt gần nhất của nhân vật chính: {main_snapshot}\n"
            "Lịch sử nhân vật chính: {main_history}\n"
            "Hành động mới nhất của nhân vật chính: {main_action}\n"
            "Cảm xúc hiện tại của nhân vật chính: {main_emotion}\n"
            "Lời thoại mới nhất của nhân vật chính: {main_dialogue}\n"
            "Chế độ tương tác: {interaction_mode}"
        ),
    ]
).partial(format_instructions=parser.get_format_instructions())


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)


def build_persona_reaction(state: GraphState) -> Dict[str, Any]:
    scenario_name = state.get("Scenario_Name", "")
    learning_objective = _ensure_text(state.get("Learning_Objective", {}))
    scene_narration = state.get("Scene_Narration", "")

    persona_profile = _ensure_text(state.get("Persona", {}))
    persona_snapshot = _format_entry(state.get("Persona_Current", {}))
    persona_history = _format_history(state.get("Persona_Dialogue_Log", []) or [])

    main_snapshot_dict = state.get("Main_Current", {}) or {}
    main_snapshot = _format_entry(main_snapshot_dict)
    main_history = _format_history(state.get("Main_Dialogue_Log", []) or [])

    main_action = main_snapshot_dict.get("action", "")
    main_emotion = main_snapshot_dict.get("emotion", "")
    main_dialogue = main_snapshot_dict.get("dialogue", "")

    interaction_mode = "respond"
    if not main_dialogue:
        interaction_mode = "initiate"

    chain = persona_prompt | llm | parser
    result = chain.invoke(
        {
            "scenario_name": scenario_name,
            "learning_objective": learning_objective,
            "scene_narration": scene_narration or "",
            "persona_profile": persona_profile,
            "persona_snapshot": persona_snapshot or "(chưa phát biểu)",
            "persona_history": persona_history or "(chưa có lịch sử)",
            "main_snapshot": main_snapshot or "(chưa xuất hiện)",
            "main_history": main_history or "(chưa có lịch sử)",
            "main_action": main_action,
            "main_emotion": main_emotion,
            "main_dialogue": main_dialogue,
            "interaction_mode": interaction_mode,
        }
    )

    persona_entry: DialogueEntry = {
        "speaker": "persona",
        "dialogue": result.persona_dialogue,
        "action": result.persona_action,
        "emotion": result.persona_emotion,
        "context": result.persona_context,
    }

    return {
        "Persona_Current": persona_entry,
        "persona_entry": persona_entry,
        "Persona_Interaction_Mode": interaction_mode,
    }
