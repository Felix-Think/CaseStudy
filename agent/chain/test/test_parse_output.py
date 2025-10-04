import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from agent.chain.parse_chain import parse_input_tool


TEST_INPUT = """
    Mục tiêu học tập: Hiểu và áp dụng các khái niệm cơ bản về lập trình Python.
    Bối cảnh mở đầu: Học sinh đã có kiến thức cơ bản về lập trình.
    Nhân vật: Một giáo viên nhiệt huyết, kiên nhẫn, luôn khuyến khích học sinh.
    """


def test_parse_input_node() -> None:
    result = parse_input_tool.invoke(TEST_INPUT)

    assert "objective_learning" in result
    assert "initial_context" in result
    assert "persona" in result
    assert isinstance(result["persona"], dict)
    assert "name" in result["persona"]
    assert "role" in result["persona"]
    assert "traits" in result["persona"]
    assert "speaking_style" in result["persona"]

    print("Kết quả parse:")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    test_parse_input_node()
