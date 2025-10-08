"""Unit tests for the scene narration chain."""

from casestudy.agent.chain import Scene_chain
from casestudy.agent.state import GraphState



def test_build_scene_narration_continuation() -> None:
    state: GraphState = {
        "Scenario_Name": "Phản ứng khẩn cấp tại hồ bơi",
        "Learning_Objective": {
            "Learning Objective": "Thực hành sơ cứu và điều phối nhân sự trong tình huống đuối nước.",
        },
        "Initial_Context": {
            "Enter Narrative": "Bạn vừa có mặt tại hiện trường, xung quanh hỗn loạn và ồn ào.",
        },
        "Persona": {
            "Role": "Thân nhân nạn nhân",
            "Personality": "Hoảng loạn, liên tục chất vấn",
        },
        "Current_Persona": {
            "role": "Thân nhân nạn nhân",
            "current_emotion": "Lo sợ",
            "current_action": "Nắm chặt tay bạn, hỏi dồn dập",
        },
        "Current_Persona_Emotion": "Lo sợ",
        "Current_Persona_Action": "Nắm chặt tay bạn, hỏi dồn dập",
        "Main_Character_Action": "Bạn quỳ xuống kiểm tra hơi thở của nạn nhân",
        "Main_Character_Emotion": "Tập trung cao độ",
        "Main_Character_Dialogue": "Xin hãy bình tĩnh, tôi sẽ xử lý ngay!",
    }

    result = Scene_chain.build_scene_narration(state)

    print("Result:", result)
if __name__ == "__main__":
    test_build_scene_narration_continuation()