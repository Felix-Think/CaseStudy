import json
import os
import sys

# === Thiết lập đường dẫn đến project gốc ===
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from agent.chain.parse_chain import parse_input_tool

# === Dữ liệu test ===
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


# === Hàm test chính ===
def test_parse_input_tool() -> None:
    """
    Kiểm thử tool parse_input_tool:
    - Gửi input mô tả case study
    - Kiểm tra các khóa chính trong output
    - In kết quả ra màn hình (JSON format)
    """

    print("\n🔍 Đang gọi parse_input_tool...\n")
    result = parse_input_tool.invoke(TEST_INPUT)

    # --- Kiểm tra các khóa bắt buộc ---
    expected_keys = [
        "Scenario Name",
        "Learning Objective",
        "Initial Context",
        "Persona (Characteristic)",
    ]

    for key in expected_keys:
        assert key in result, f"❌ Thiếu khóa bắt buộc: {key}"

    # --- Kiểm tra kiểu dữ liệu ---
    assert isinstance(result["Learning Objective"], dict), "❌ 'Learning Objective' phải là dict"
    assert isinstance(result["Initial Context"], dict), "❌ 'Initial Context' phải là dict"
    assert isinstance(result["Persona (Characteristic)"], dict), "❌ 'Persona (Characteristic)' phải là dict"
    
    # --- In kết quả JSON ---
    print("✅ Kết quả parse thành công:\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # --- Kiểm tra nội dung cơ bản ---
    assert len(result["Scenario Name"]) > 0, "❌ 'Scenario Name' rỗng"
    assert "Learning Objective" in result["Learning Objective"], "❌ Thiếu khóa con trong 'Learning Objective'"
    assert "Enter Narrative" in result["Initial Context"], "❌ Thiếu khóa con trong 'Initial Context'"

    print("\n🎯 Test hoàn tất — tất cả kiểm tra đều đạt.\n")


# === Cho phép chạy độc lập ===
if __name__ == "__main__":
    test_parse_input_tool()
