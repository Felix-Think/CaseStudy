"""Graph node that updates persona dialogue state."""

from typing import Any, Dict

from agent.chain.Persona_chain import build_persona_reaction
from agent.state import DialogueEntry, GraphState


def persona_node(state: GraphState) -> GraphState:
    """Generate persona's next turn and update dialogue logs."""
    reaction: Dict[str, Any] = build_persona_reaction(state)

    persona_entry = reaction.get("persona_entry")
    if not persona_entry:
        # Fallback: nothing new; return state untouched.
        return state

    # Update current snapshot for persona.
    updated_state: GraphState = {
        **state,
        "Persona_Current": persona_entry,  # type: ignore[assignment]
    }

    # Append to dialogue history (create if missing).
    history = list(state.get("Persona_Dialogue_Log", []))
    history.append(persona_entry)  # type: ignore[arg-type]
    updated_state["Persona_Dialogue_Log"] = history  # type: ignore[index]

    # Expose interaction mode if downstream logic needs it.
    if "Persona_Interaction_Mode" in reaction:
        updated_state["Persona_Interaction_Mode"] = reaction["Persona_Interaction_Mode"]

    return updated_state


if __name__ == "__main__":
    demo_state: GraphState = {
        "Scenario_Name": "Ca trực hồ bơi cuối tuần",
        "Learning_Objective": {"Learning Objective": "Huấn luyện xử lý cấp cứu trong môi trường đông người."},
        "Initial_Context": {"Enter Narrative": "Bạn vừa đến khu vực nạn nhân bị đuối nước."},
        "Scene_Narration": "Bạn quỳ xuống bên cạnh nạn nhân, nước vẫn nhỏ từng giọt xuống nền gạch.",
        "Persona": {
            "Role": "Thân nhân nạn nhân",
            "Background": "Mẹ của bé trai đang hoảng loạn",
            "Personality": "Lo lắng, dễ xúc động",
        },
        "Persona_Current": {},
        "Persona_Dialogue_Log": [],
        "Main_Current": {
            "speaker": "main",
            "dialogue": "Chị bình tĩnh, để tôi kiểm tra mạch đã.",
            "action": "Đặt tay lên cổ nạn nhân",
            "emotion": "Tập trung",
            "context": "Giọng kiềm chế nhưng nhanh gọn",
        },
        "Main_Dialogue_Log": [],
    }

    new_state = persona_node(demo_state)
    print("Persona turn:\n", new_state.get("Persona_Current"))
    print("History size:", len(new_state.get("Persona_Dialogue_Log", [])))

