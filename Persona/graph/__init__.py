from typing import Any

from langgraph.graph import END, StateGraph

from Persona.graph.nodes import generate_personas_node, load_case_node
from Persona.state import PersonaState


def build_persona_graph() -> Any:
    """Compose the LangGraph pipeline for persona enrichment."""
    graph = StateGraph(PersonaState)

    graph.add_node("load_case", load_case_node)
    graph.add_node("generate_personas", generate_personas_node)

    graph.set_entry_point("load_case")
    graph.add_edge("load_case", "generate_personas")
    graph.add_edge("generate_personas", END)

    return graph.compile()


__all__ = ["build_persona_graph"]

