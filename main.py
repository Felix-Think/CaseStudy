"""Simple CLI to interact with the supervisor graph."""

from typing import Any

from agent.graph import build_supervisor_graph
from agent.state import GraphState


def _print_scene(state: GraphState) -> None:
    scene = state.get("Scene_Narration", "")
    focus = state.get("Narrator_Focus", "")
    if scene:
        print("\n--- Scene Narration ---")
        print(scene)
    if focus:
        print("\n--- Narrator Focus ---")
        print(focus)


def _print_persona(state: GraphState) -> None:
    persona_entry = state.get("Persona_Current") or {}
    dialogue = persona_entry.get("dialogue") if isinstance(persona_entry, dict) else None
    action = persona_entry.get("action") if isinstance(persona_entry, dict) else None
    if dialogue or action:
        print("\n--- Persona Response ---")
        if dialogue:
            print(f"Lời thoại: {dialogue}")
        if action:
            print(f"Hành động: {action}")


def main() -> None:
    app = build_supervisor_graph()

    state: GraphState = {
        "Persona_Dialogue_Log": [],
        "Main_Dialogue_Log": [],
    }

    print("Nhập bối cảnh ban đầu (để trống để thoát):")
    context = input(">> ").strip()
    if not context:
        print("Không có bối cảnh đầu vào. Thoát.")
        return

    state["raw_user_input"] = context
    state = app.invoke(state)

    _print_scene(state)
    _print_persona(state)

    print("\nBắt đầu hội thoại. Để trống để kết thúc.")

    while True:
        user_turn = input("\nBạn: ").strip()
        if not user_turn:
            print("Kết thúc hội thoại.")
            break

        state["raw_user_turn"] = user_turn
        state = app.invoke(state)

        _print_scene(state)
        _print_persona(state)


if __name__ == "__main__":
    main()
