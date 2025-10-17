from __future__ import annotations

from langchain_core.runnables import RunnableConfig
from ..memory import LogicMemory
from ..state import RuntimeState
from typing import Any

def build_responder_node(
    logic_memory: LogicMemory,
    responder_chain,
) -> Any:
    """
    Produce facilitator feedback via the responder chain.
    """

    def respond(state: RuntimeState, _: RunnableConfig = None) -> RuntimeState:
        event = logic_memory.get_event(state.current_event)
        persona_overview = [
            f"{persona.name} ({persona.role}) - cảm xúc: {persona.emotion}"
            for persona in state.active_personas.values()
        ]

        ai_reply = responder_chain(
            {
                "event_title": event.get("title", state.current_event) if event else state.current_event,
                "scene_summary": state.scene_summary or "Chưa có dữ liệu.",
                "required_actions": event.get("required_actions", []) if event else [],
                "persona_overview": "; ".join(persona_overview) or "Không có.",
                "dialogue_history": state.dialogue_history,
                "policy_flags": state.policy_flags,
                "user_action": state.user_action or "Chưa ghi nhận.",
                "turn_count": state.turn_count,
                "max_turns": state.max_turns,
                "system_notice": state.system_notice,
            }
        )

        state.ai_reply = ai_reply
        if not state.system_notice:
            state.turn_count = state.turn_count + 1
        return state

    return respond
