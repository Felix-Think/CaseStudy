from __future__ import annotations

from langchain_core.runnables import RunnableConfig
from ..memory import LogicMemory
from ..state import RuntimeState
from typing import Any

def build_transition_node(logic_memory: LogicMemory) -> Any:
    """
    Decide the next canon event based on evaluation status.
    """

    def transition(state: RuntimeState, _: RunnableConfig = None) -> RuntimeState:
        event = logic_memory.get_event(state.current_event)
        if not event:
            return state

        status = state.event_summary.get(state.current_event, "pending")

        if status == "pass" and event.get("on_success"):
            state.current_event = event["on_success"]
        elif status == "fail" and event.get("on_fail"):
            state.current_event = event["on_fail"]

        return state

    return transition
