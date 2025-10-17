from __future__ import annotations

from langchain_core.runnables import RunnableConfig

from ..runtime_store import RuntimeStateStore
from ..state import RuntimeState
from typing import Any

def build_ingress_node(
    state_store: RuntimeStateStore,
    *,
    default_event: str,
) -> Any:
    """
    Load an existing runtime state if available; otherwise initialise with defaults.
    """

    def ingress(state: RuntimeState, config: RunnableConfig = None) -> RuntimeState:
        cfg = dict(config or {})
        incoming_action = state.user_action

        if not cfg.get("reset_state"):
            stored_state = state_store.load()
            if stored_state:
                if incoming_action:
                    stored_state.user_action = incoming_action
                return stored_state

        start_event = cfg.get("start_event") or default_event
        state.current_event = start_event
        return state

    return ingress
