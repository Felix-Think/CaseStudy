"""Node that calls the canon event generation chain and stores results in state."""

from typing import Dict, Any, List

from Skeleton.graph.chain import build_canon_plan
from Skeleton.state import SkeletonState


def _summarize_context(context: Dict[str, Any]) -> str:
    if not context:
        return "(không có thông tin bối cảnh)"

    parts: List[str] = []
    scene = context.get("scene") or {}
    if scene:
        time = scene.get("time")
        location = scene.get("location")
        weather = scene.get("weather")
        snippets = []
        if time:
            snippets.append(f"Thời gian: {time}")
        if location:
            snippets.append(f"Địa điểm: {location}")
        if weather:
            snippets.append(f"Thời tiết: {weather}")
        if snippets:
            parts.append("Cảnh: " + "; ".join(snippets))

    index_event = context.get("index_event") or {}
    if index_event:
        summary = index_event.get("summary")
        state = index_event.get("current_state")
        if summary:
            parts.append(f"Sự kiện chính: {summary}")
        if state:
            parts.append(f"Tình trạng hiện tại: {state}")

    constraints = context.get("constraints") or []
    if constraints:
        joined = "; ".join(str(item) for item in constraints)
        parts.append(f"Hạn chế: {joined}")

    target = context.get("handover_target")
    if target:
        parts.append(f"Mục tiêu bàn giao: {target}")

    return "\n".join(parts) if parts else "(không có thông tin bối cảnh)"


def generate_canon_node(state: SkeletonState) -> SkeletonState:
    """Generate canon events using the LLM chain."""
    case_id = state.get("case_id", "")
    topic = state.get("topic", "")
    language = state.get("language", "vi-VN")
    initial_context = state.get("initial_context", {})
    learning_objectives = state.get("learning_objectives", [])
    personas = state.get("personas", [])

    context_summary = _summarize_context(initial_context)

    plan: Dict[str, Any] = build_canon_plan(
        case_id=case_id,
        topic=topic,
        language=language,
        objectives=learning_objectives,
        personas=personas,
        context_summary=context_summary,
    )

    return {
        **state,
        "canon_events": plan.get("canon_events", []),
        "telemetry": plan.get("telemetry", {}),
    }
