from typing import Any

from langgraph.graph import END, StateGraph


from agent.nodes.parse_node import parse_input_node
from agent.nodes.parse_user_turn_node import parse_user_turn_node
from agent.nodes.persona_node import persona_node
from agent.nodes.scene_node import scene_node
from agent.state import GraphState


def _supervisor_node(state: GraphState) -> GraphState:
    """Entry node – decide next route and attach diagnostic info."""
    if state.get("raw_user_turn"):
        supervisor_route = "parse_user_turn"
    elif state.get("raw_user_input") and not (state.get("Scenario_Name") or "").strip():
        supervisor_route = "parse_context"
    else:
        supervisor_route = state.get("Supervisor_Route")
        if supervisor_route not in {"parse_context", "parse_user_turn", "scene"}:
            supervisor_route = "scene"

    return {
        **state,
        "Supervisor_Route": supervisor_route,
    }


def _route_initial(state: GraphState) -> str:
    supervisor_route = state.get("Supervisor_Route")
    if supervisor_route in {"parse_context", "parse_user_turn", "scene"}:
        return supervisor_route

    if state.get("raw_user_turn"):
        return "parse_user_turn"
    if state.get("raw_user_input") and not (state.get("Scenario_Name") or "").strip():
        return "parse_context"
    return "scene"


def _has_persona(state: GraphState) -> bool:
    if state.get("Persona_Present") is True:
        return True
    persona = state.get("Persona") or {}
    return bool(persona and any(value for value in persona.values()))


def _route_after_context(state: GraphState) -> str:
    return "persona" if _has_persona(state) else "scene"


def _route_after_user_turn(state: GraphState) -> str:
    return "persona" if _has_persona(state) else "scene"


def build_supervisor_graph() -> Any:
    """Create the LangGraph workflow that supervises parsing and narration."""
    graph = StateGraph(GraphState)

    graph.add_node("supervisor", _supervisor_node)
    graph.add_node("parse_context", parse_input_node)
    graph.add_node("parse_user_turn", parse_user_turn_node)
    graph.add_node("persona", persona_node)
    graph.add_node("scene", scene_node)

    graph.set_entry_point("supervisor")

    graph.add_conditional_edges(
        "supervisor",
        _route_initial,
        {
            "parse_context": "parse_context",
            "parse_user_turn": "parse_user_turn",
            "scene": "scene",
        },
    )

    graph.add_conditional_edges(
        "parse_context",
        _route_after_context,
        {
            "persona": "persona",
            "scene": "scene",
        },
    )

    graph.add_conditional_edges(
        "parse_user_turn",
        _route_after_user_turn,
        {
            "persona": "persona",
            "scene": "scene",
        },
    )

    graph.add_edge("persona", "scene")
    graph.add_edge("scene", END)

    app = graph.compile()

    graph_view = app.get_graph()
    try:
        draw_mermaid_png = getattr(graph_view, "draw_mermaid_png", None)
        if callable(draw_mermaid_png):
            draw_mermaid_png(output_file_path="supervisor_graph.png")
            print("Supervisor graph diagram saved to supervisor_graph.png")
    except Exception as exc:  # pragma: no cover
        print(f"Could not render graph diagram: {exc}")

    return app




if __name__ == "__main__":
    build_supervisor_graph()
    print("Supervisor graph compiled. Ready for invocation.")
