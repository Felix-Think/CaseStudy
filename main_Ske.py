"""CLI utility to load a case JSON, generate the skeleton plan and persist it."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Iterable

from Skeleton.graph import build_skeleton_graph
from Skeleton.state import SkeletonState


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
    trigger = event.get("trigger", "")
    actions = event.get("required_actions", [])
    phase_id = event.get("phase_id", "")
    timeout_turn = event.get("timeout_turn")
    turns_text = f"{timeout_turn}" if timeout_turn is not None else "?"
    npc_lines = event.get("npc_lines", [])
    npc_text = (
        "\n        NPC lines: " + " | ".join(str(line) for line in npc_lines)
        if npc_lines
        else ""
    )
    return (
        f"- {event_id}: {title}\n"
        f"    Phase: {phase_id} | Timeout turns: {turns_text}\n"
        f"    Trigger: {trigger}\n"
        f"    Actions: {', '.join(actions) if actions else '(không nêu)'}"
        f"{npc_text}"
    )


def _default_output_path(case_id: str) -> Path:
    safe_case = case_id or "skeleton"
    return Path(f"{safe_case}_skeleton.json")


def _persist_output(state: SkeletonState, output_path: Path) -> None:
    payload = {
        "case_id": state.get("case_id"),
        "canon_events": state.get("canon_events", []),
        "telemetry": state.get("telemetry", {}),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)
    print(f"\nĐã lưu skeleton JSON tại: {output_path}")


def main() -> None:
    graph = build_skeleton_graph()

    args = sys.argv[1:]
    case_path = args[0] if len(args) >= 1 else ""
    output_path_arg = args[1] if len(args) >= 2 else ""

    state: SkeletonState = {}
    if case_path:
        state["case_json_path"] = str(Path(case_path).expanduser())

    state = graph.invoke(state)  # type: ignore[assignment]

    case_id = state.get("case_id", "(unknown)")
    print("Skeleton generated for case:", case_id)

    canon_events = state.get("canon_events", [])
    _print_section("Canon Events", (_format_event(evt) for evt in canon_events))

    telemetry = state.get("telemetry", {})
    telemetry_lines = []
    if telemetry:
        telemetry_lines.append(f"- log_events: {telemetry.get('log_events')}")
        metrics = telemetry.get("metrics", [])
        if metrics:
            telemetry_lines.append(f"- metrics: {', '.join(metrics)}")
        for rollup in telemetry.get("phase_rollup", []):
            telemetry_lines.append(
                f"- phase_rollup {rollup.get('phase_id')}: metrics={rollup.get('metrics')} targets={rollup.get('targets')}"
            )
    _print_section("Telemetry", telemetry_lines)

    output_path = (
        Path(output_path_arg).expanduser()
        if output_path_arg
        else _default_output_path(str(state.get("case_id", "skeleton")))
    )
    _persist_output(state, output_path)


if __name__ == "__main__":
    main()
