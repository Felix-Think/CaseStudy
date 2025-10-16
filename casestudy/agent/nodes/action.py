from __future__ import annotations

from langchain_core.runnables import RunnableConfig
from ..memory import LogicMemory
from ..state import RuntimeState


def build_action_node(
    logic_memory: LogicMemory,
    action_chain,
) -> Any:
    """
    Evaluate learner actions against the current canon event requirements.
    """

    def evaluate(state: RuntimeState, _: RunnableConfig = None) -> RuntimeState:
        event = logic_memory.get_event(state.current_event)
        required_actions = event.get("required_actions", []) if event else []

        result = action_chain(
            {
                "user_action": state.user_action,
                "required_actions": required_actions,
            }
        )

        state.event_summary[state.current_event] = result.get("status", "pending")
        state.event_summary[f"{state.current_event}_matched"] = result.get("matched_actions", [])
        state.event_summary[f"{state.current_event}_scores"] = result.get("scores", [])
        return state

    return evaluate
