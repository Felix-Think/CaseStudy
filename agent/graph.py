from pathlib import Path
from typing import Optional, Union

from langgraph.graph import END, StateGraph

from agent.const import GENERATE_SCENE, PARSE_OUTPUT
from agent.nodes.generator_node import generate_scene_node
from agent.nodes.parse_node import parse_input_node
from agent.state import GraphState



def build_case_study_graph(save_path: Optional[Union[str, Path]] = None):
    """wire up the LangGraph workflow and optionally save the diagram."""
    builder = StateGraph(GraphState)

    builder.add_node(PARSE_OUTPUT, parse_input_node)
    builder.add_node(GENERATE_SCENE, generate_scene_node)

    builder.set_entry_point(PARSE_OUTPUT)
    builder.add_edge(PARSE_OUTPUT, GENERATE_SCENE)
    builder.add_edge(GENERATE_SCENE, END)

    app = builder.compile()

    app.get_graph().draw_mermaid_png(output_file_path= save_path) if save_path else None

    return app

if __name__ == "__main__":
    app = build_case_study_graph(save_path="case_study_graph.png")
    initial_state: GraphState = {
        "raw_user_input": "Bối cảnh: 16:30 tại hồ bơi công cộng. Một bé trai 11 tuổi vừa được kéo lên bờ, đang ho sặc sụa và có lúc lịm đi. Người kể chuyện: Bạn là người bác sĩ cấp cứu từ bệnh viện vừa đến hiện trường để tiến hành sơ cứu."
    }
    final_state = app.invoke(initial_state)
    print("Kết quả graph:")
    print(final_state.get("generated_scene", "Không nhận được generated_scene."))
    print("Toàn bộ trạng thái cuối cùng:")
    print(final_state)