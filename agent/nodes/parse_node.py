from typing import Dict, Any
import os
import sys
from agent.chain.parse_chain import parse_input_tool
from agent.state import GraphState


# === Thiết lập đường dẫn đến project gốc ===
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

def parse_input_node(state: GraphState) -> GraphState:
    """Parse raw user input into the structured graph state."""
    raw_user_input = state.get("raw_user_input", "")
    if not raw_user_input:
        raise ValueError("raw_user_input is required in the state.")

    parsed: Dict[str, Any] = parse_input_tool.invoke(raw_user_input)

    scenario_name = parsed.get("Scenario Name", "")
    learning_objective = parsed.get("Learning Objective", {})
    initial_context = parsed.get("Initial Context", {})
    persona_characteristic = parsed.get("Persona (Characteristic)", {})
    current_persona_emotion = parsed.get("Current_Persona_Emotion", "")
    current_persona_action = parsed.get("Current_Persona_Action", "")

    return {
        **state,
        "Scenario_Name": scenario_name,
        "Learning_Objective": learning_objective,
        "Initial_Context": initial_context,
        "Persona": persona_characteristic,
        "Current_Persona_Emotion": current_persona_emotion,
        "Current_Persona_Action": current_persona_action,
    }


if __name__ == "__main__":
    TEST_INPUT = """
Tên kịch bản: Phản ứng khẩn cấp với hành khách bị đuối nước

Mục tiêu học tập:
Đánh giá khả năng của học viên trong việc thực hiện các bước sơ cứu ban đầu một cách chính xác và kịp thời cho nạn nhân đuối nước,
đồng thời kích hoạt hệ thống ứng phó khẩn cấp và giao tiếp hiệu quả trong tình huống căng thẳng.

Bối cảnh ban đầu:
Bạn là một **nhân viên cứu hộ** đang làm việc tại một **hồ bơi công cộng** đông đúc vào cuối tuần.
Bạn đang tuần tra khu vực và quan sát các hoạt động bơi lội. 
Đột nhiên, bạn nghe thấy tiếng la hét và một số người đang chỉ về phía cuối hồ. 
Bạn thấy một **người lớn tuổi** đang có dấu hiệu **chìm, vùng vẫy yếu ớt** ở khu vực sâu của hồ. 
Bạn là người đầu tiên tiếp cận hiện trường.

Nhân vật phụ (persona):
- Vai trò: [ Thân nhân của nạn nhân ]
- Bối cảnh: Người này là mẹ của nạn nhân. Họ đang đứng gần đó khi sự việc xảy ra và vừa nhận ra con mình đang gặp nguy hiểm.
- Tính cách: Họ cực kỳ **hoảng loạn, lo lắng** và **mất bình tĩnh**. Họ sẽ **liên tục đặt câu hỏi, gây áp lực** và **cản trở** một cách vô ý thức quá trình sơ cứu của bạn vì sự lo lắng thái quá cho người thân.
- Ghi chú: Tuyệt đối không được tiết lộ tên của thân nhân này trong bất kỳ trường hợp nào.
"""
    initial_state = {"raw_user_input": TEST_INPUT}
    new_state = parse_input_node(initial_state)
    print(new_state)
