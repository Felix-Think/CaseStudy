"""Node that transforms raw personas into detailed profiles via LLM."""

from __future__ import annotations

from typing import Dict, Any, List

from Persona.graph.chain import build_persona_plan
from Persona.state import PersonaState


def generate_personas_node(state: PersonaState) -> PersonaState:
    """Enrich personas with detailed attributes using the LLM chain."""
    case_id = state.get("case_id", "")
    topic = state.get("topic", "")
    language = state.get("language", "vi-VN")
    context = state.get("initial_context", {})
    personas: List[Dict[str, Any]] = state.get("personas", [])

    plan = build_persona_plan(
        case_id=case_id,
        topic=topic,
        language=language,
        context=context,
        personas=personas,
    )

    return {
        **state,
        "persona_profiles": plan.get("personas", []),
    }

