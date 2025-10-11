from typing import Any

from langgraph.graph import END, StateGraph

from Skeleton.graph.nodes import generate_canon_node, load_case_node
from Skeleton.state import SkeletonState


def build_skeleton_graph() -> Any:
    """Create the LangGraph pipeline for loading a case and generating canon outline."""
    graph = StateGraph(SkeletonState)

    graph.add_node("load_case", load_case_node)
    graph.add_node("generate_canon", generate_canon_node)

    graph.set_entry_point("load_case")
    graph.add_edge("load_case", "generate_canon")
    graph.add_edge("generate_canon", END)

    return graph.compile()


__all__ = ["build_skeleton_graph"]
