from __future__ import annotations

from langchain_core.runnables import RunnableConfig

from ..state import RuntimeState


def _append(history, speaker, content):
    if not content:
        return
    if history and history[-1] == {"speaker": speaker, "content": content}:
        return
    history.append({"speaker": speaker, "content": content})


def build_state_update_node(*, policy_penalty: float = 0.1) -> Any:
    """
    Synchronise dialogue history and apply simple trust adjustments.
    """

    def update(state: RuntimeState, _: RunnableConfig = None) -> RuntimeState:
        _append(state.dialogue_history, "user", state.user_action)
        _append(state.dialogue_history, "ai", state.ai_reply)

        num_flags = len(state.policy_flags or [])
        if num_flags:
            for persona in state.active_personas.values():
                persona.trust = max(0.0, persona.trust - policy_penalty * num_flags)
                persona.emotion = persona.emotion or "neutral"
                if persona.trust < 0.3:
                    persona.emotion = "lo lắng"

        state.user_action = None
        return state

    return update
