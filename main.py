from agent.graph import build_case_study_graph
from agent.state import GraphState


def run_case_study_builder(raw_user_input: str) -> GraphState:
    """Invoke the case-study workflow from the raw instructor prompt."""
    app = build_case_study_graph(save_path="case_study_graph.png")
    initial_state: GraphState = {"raw_user_input": raw_user_input}
    return app.invoke(initial_state)


if __name__ == "__main__":
    user_prompt = input("Bối cảnh: 16:30 tại hồ bơi công cộng. Một bé trai 11 tuổi vừa được kéo lên bờ, "
            "đang ho sặc sụa và có lúc lịm đi. Người kể chuyện: Bạn là người bác sĩ cấp cứu từ bệnh viện vừa đến hiện trường để tiến hành sơ cứu.").strip()
    if not user_prompt:
        raise SystemExit("Vui lòng nhập yêu cầu trước khi chạy workflow.")

    final_state = run_case_study_builder(user_prompt)
    print("Kết quả graph:")
    print("Toàn bộ trạng thái cuối cùng:")
    print(final_state)