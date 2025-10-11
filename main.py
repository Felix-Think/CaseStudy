"""CLI demo for Script Generator using LangGraph."""

from typing import Any

from ScriptGenerator.graph import build_script_generator_graph
from ScriptGenerator.state import ScriptGeneratorState


DEFAULT_BRIEF = """Phản ứng khẩn cấp với hành khách bị đuối nước.
Mục tiêu học tập:Đánh giá khả năng của học viên trong việc thực hiện các bước sơ cứu ban đầu một cách chính xác và kịp thời cho nạn nhân đuối nước,đồng thời kích hoạt hệ thống ứng phó khẩn cấp và giao tiếp hiệu quả trong tình huống căng thẳng.
Bối cảnh ban đầu:Bạn là một nhân viên cứu hộ đang làm việc tại một hồ bơi công cộng đông đúc vào cuối tuần.Bạn đang tuần tra khu vực và quan sát các hoạt động bơi lội. Đột nhiên, bạn nghe thấy tiếng la hét và một số người đang chỉ về phía cuối hồ. Bạn thấy một người lớn tuổi đang có dấu hiệu chìm, vùng vẫy yếu ớt ở khu vực sâu của hồ. Bạn là người đầu tiên tiếp cận hiện trường.
Nhân vật phụ (persona):- Vai trò: [ Thân nhân của nạn nhân ]- Bối cảnh: Người này là mẹ của nạn nhân. Họ đang đứng gần đó khi sự việc xảy ra và vừa nhận ra con mình đang gặp nguy hiểm.- Tính cách: Họ cực kỳ hoảng loạn, lo lắng và mất bình tĩnh. Họ sẽ liên tục đặt câu hỏi, gây áp lực và cản trở một cách vô ý thức quá trình sơ cứu của bạn vì sự lo lắng thái quá cho người thân.
"""


def _build_app() -> Any:
    return build_script_generator_graph()


def _initial_state(brief: str) -> ScriptGeneratorState:
    return {
        "raw_brief": brief.strip(),
        "script_history": [],
    }


def _print_segment(state: ScriptGeneratorState) -> None:
    script = state.get("script_output", "")
    if script:
        print("\n--- Đoạn kịch bản ---")
        print(script)
    else:
        print("\n(Chưa tạo được đoạn kịch bản)")

    history = state.get("script_history", [])
    if history:
        print(f"\n(Đã sinh tổng cộng {len(history)} đoạn)")


def main() -> None:
    app = _build_app()
    state = _initial_state(DEFAULT_BRIEF)

    print("=== Script Generator Demo ===")
    print("Nhập 'START' để chạy bối cảnh mở đầu.")
    print("Sau đó nhập lời thoại của bạn để script tiếp tục (ENTER trống để thoát).")

    while True:
        user_input = input("\nBạn: ").strip()
        if not user_input:
            print("Kết thúc demo.")
            break

        if user_input.upper() == "START":
            state["latest_user_response"] = ""
        else:
            state["latest_user_response"] = user_input

        state = app.invoke(state)  # type: ignore[assignment]
        state["raw_brief"] = ""  # tránh parse lại trong vòng lặp kế tiếp
        _print_segment(state)


if __name__ == "__main__":
    main()
