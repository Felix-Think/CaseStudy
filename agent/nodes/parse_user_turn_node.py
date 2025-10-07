"""Normalize the latest user turn into DialogueEntry format."""

from typing import Dict, Any

from agent.state import DialogueEntry, GraphState


def parse_user_turn_node(state: GraphState) -> GraphState:
    """Capture the raw user turn as the main character's latest dialogue entry."""
    raw_turn = (state.get("raw_user_turn") or "").strip()
    if not raw_turn:
        raise ValueError("raw_user_turn is required for parse_user_turn_node")

    entry: DialogueEntry = {
        "speaker": "main",
        "dialogue": raw_turn,
        "action": state.get("Main_Character_Action", ""),
        "emotion": state.get("Main_Character_Emotion", ""),
        "context": state.get("Main_Character_Dialogue_Context", ""),
    }

    history = list(state.get("Main_Dialogue_Log", []))
    history.append(entry)

    updated_state: Dict[str, Any] = {
        **state,
        "Main_Current": entry,
        "Main_Dialogue_Log": history,
        "Main_Character_Dialogue": raw_turn,
        "raw_user_turn": "",
    }

    # Ensure legacy fields are set even if not provided by caller.
    updated_state.setdefault("Main_Character_Action", entry["action"])
    updated_state.setdefault("Main_Character_Emotion", entry["emotion"])

    return updated_state


if __name__ == "__main__":
    test_state: GraphState = {
        "raw_user_turn": "Tôi sẽ kiểm tra đường thở ngay.",
        "Main_Dialogue_Log": [],
    }
    new_state = parse_user_turn_node(test_state)
    print(new_state["Main_Current"])
