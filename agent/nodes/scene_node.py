"""Graph node that generates narrated scene context."""

from typing import Dict, Any

from agent.chain.Scene_chain import build_scene_narration
from agent.state import GraphState


def scene_node(state: GraphState) -> GraphState:
    """Produce or refresh the narrative context based on current dialogue state."""
    narration: Dict[str, Any] = build_scene_narration(state)

    return {
        **state,
        "Scene_Narration": narration.get("Scene_Narration", ""),
        "Narrator_Focus": narration.get("Narrator_Focus", ""),
        "Story_Phase": narration.get("Story_Phase", ""),
        "Narrative_Mode": narration.get("Narrative_Mode", ""),
        "Persona_Present": narration.get("Persona_Present", False),
    }


if __name__ == "__main__":
    demo_state: GraphState = {
        "Scenario_Name": "Phản ứng khẩn cấp tại hồ bơi",
        "Learning_Objective": {
            "Learning Objective": "Thực hành sơ cứu an toàn và điều phối nhân sự trong tình huống đuối nước.",
        },
        "Initial_Context": {
            "Enter Narrative": "Một buổi chiều cuối tuần, khu hồ bơi đông nghịt và hỗn loạn sau tiếng la hét.",
        },
        "Persona": {
            "Role": "Thân nhân nạn nhân",
            "Personality": "Hoảng loạn",
        },
        "Persona_Current": {
            "speaker": "persona",
            "dialogue": "Làm ơn cứu con tôi với!",
            "action": "Bấu chặt lấy tay bạn",
            "emotion": "Hoảng loạn",
            "context": "Đứng sát bên bạn, run rẩy",
        },
        "Persona_Dialogue_Log": [],
        "Main_Current": {
            "speaker": "main",
            "dialogue": "Chị bình tĩnh, tôi đang kiểm tra hơi thở",
            "action": "Đặt tai sát miệng nạn nhân",
            "emotion": "Tập trung",
            "context": "Quỳ một gối trên nền gạch ướt",
        },
        "Main_Dialogue_Log": [],
    }

    updated_state = scene_node(demo_state)
    print("Scene narration:\n", updated_state.get("Scene_Narration"))
    print("Narrator focus:\n", updated_state.get("Narrator_Focus"))
    print("Narrative mode:", updated_state.get("Narrative_Mode"))
