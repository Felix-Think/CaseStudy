from __future__ import annotations

from langchain_core.runnables import RunnableConfig

from ..memory import LogicMemory
from ..runtime_store import RuntimeStateStore
from ..state import RuntimeState
from typing import Any

def build_ingress_node(
    state_store: RuntimeStateStore,
    logic_memory: LogicMemory,
    *,
    default_event: str,
) -> Any:
    """
    Load an existing runtime state if available; otherwise initialise with defaults.
    """

    def _apply_event_limits(state: RuntimeState, event_id: str) -> None:
        event = logic_memory.get_event(event_id) if event_id else None
        state.max_turns = event.get("timeout_turn", 0) if event else 0

    def ingress(state: RuntimeState, config: RunnableConfig = None) -> RuntimeState:
        cfg = dict(config or {})
        incoming_action = state.user_action

        if not cfg.get("reset_state"):
            stored_state = state_store.load()
            if stored_state:
                _apply_event_limits(stored_state, stored_state.current_event)
                if incoming_action:
                    stored_state.user_action = incoming_action
                return stored_state

        start_event = cfg.get("start_event") or default_event
        state.current_event = start_event
        state.turn_count = 0
        state.system_notice = None
        _apply_event_limits(state, start_event)
        return state

    return ingress
