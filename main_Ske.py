"""CLI utility to load a case JSON, generate the skeleton plan and persist it."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from Skeleton.graph import build_skeleton_graph
from Skeleton.state import SkeletonState


CASE_JSON_PATH = Path("data/drown.json")


def _print_section(title: str, lines: Iterable[str]) -> None:
    entries = [line for line in lines if str(line).strip()]
    print(f"\n=== {title} ===")
    if not entries:
        print("(trống)")
        return
    for line in entries:
        print(line)


def _format_event(event: dict[str, Any]) -> str:
    event_id = event.get("id", "")
    title = event.get("title", "")
    description = event.get("description", "")
    actions = event.get("required_actions", [])
    success = event.get("success_criteria", [])
    preconditions = event.get("preconditions", [])
    on_success = event.get("on_success")
    on_fail = event.get("on_fail")
    npc_list = event.get("npc_appearance", [])
    timeout_turn = event.get("timeout_turn")

    preconditions_text = ", ".join(preconditions) if preconditions else "(không có)"
    success_text = ", ".join(success) if success else "(không nêu)"
    on_success_text = on_success or "(kết thúc)"
    on_fail_text = on_fail or f"{event_id}_RETRY"
    timeout_text = str(timeout_turn) if timeout_turn is not None else "(không đặt)"

    npc_lines: list[str] = []
    for persona in npc_list:
        persona_id = persona.get("persona_id") or ""
        role = persona.get("role") or ""
        note = persona.get("note") or ""
        detail = "; ".join(part for part in [role, note] if part)
        label = persona_id or "(ẩn danh)"
        npc_lines.append(f"{label}: {detail}" if detail else label)
    npc_text = " | ".join(npc_lines) if npc_lines else "(không nêu)"

    return (
        f"- {event_id}: {title}\n"
        f"    Mô tả: {description}\n"
        f"    Preconditions: {preconditions_text}\n"
        f"    Actions: {', '.join(actions) if actions else '(không nêu)'}\n"
        f"    Success: {success_text}\n"
        f"    Timeout turn: {timeout_text}\n"
        f"    On success: {on_success_text}\n"
        f"    On fail: {on_fail_text}\n"
        f"    NPC: {npc_text}"
    )


def _default_output_path(case_id: str) -> Path:
    safe_case = case_id or "skeleton"
    return Path(f"{safe_case}_skeleton.json")


def _persist_output(state: SkeletonState, output_path: Path) -> None:
    payload = {
        "case_id": state.get("case_id"),
        "canon_events": state.get("canon_events", []),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)
    print(f"\nĐã lưu skeleton JSON tại: {output_path}")


def main() -> None:
    graph = build_skeleton_graph()

    state: SkeletonState = {
        "case_json_path": str(CASE_JSON_PATH.expanduser()),
    }

    state = graph.invoke(state)  # type: ignore[assignment]

    case_id = state.get("case_id", "(unknown)")
    print("Skeleton generated for case:", case_id)

    canon_events = state.get("canon_events", [])
    _print_section("Canon Events", (_format_event(evt) for evt in canon_events))

    output_path = _default_output_path(str(state.get("case_id", "skeleton")))
    _persist_output(state, output_path)


if __name__ == "__main__":
    main()

