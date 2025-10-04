from typing import Dict, Any

from agent.chain.parse_chain import parse_input_tool
from agent.state import GraphState

def parse_input_node(state: GraphState) -> GraphState:
    raw_user_input  = state.get("raw_user_input", "")
    if not raw_user_input:
        raise ValueError("raw_user_input is required in the state.")
    
    parsed: Dict[str, Any] = parse_input_tool.invoke(raw_user_input)
    return {
        **state,
        "objective_learning": parsed.get("objective_learning", ""),
        "initial_context": parsed.get("initial_context", ""),
        "persona": parsed.get("persona", {}),
    }

if __name__ == "__main__":
    test_input = """
    Mục tiêu học tập: Hiểu và áp dụng các khái niệm cơ bản về lập trình Python.
    Bối cảnh mở đầu: Học sinh đã có kiến thức cơ bản về lập trình.
    Nhân vật: Một giáo viên nhiệt huyết, kiên nhẫn, luôn khuyến khích học sinh.
    """
    initial_state = {"raw_user_input": test_input}
    new_state = parse_input_node(initial_state)
    print(new_state)