"""CLI utility to generate enriched personas from a case JSON file."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Mapping, Any

from Persona.graph import build_persona_graph
from Persona.state import PersonaState


def _print_section(title: str, lines: Iterable[str]) -> None:
    entries = [line for line in lines if str(line).strip()]
    print(f"\n=== {title} ===")
    if not entries:
        print("(trống)")
        return
    for line in entries:
        print(line)


def _format_persona(persona: Mapping[str, Any]) -> str:
    pid = persona.get("id", "")
    name = persona.get("name", "")
    role = persona.get("role", "")
    age = persona.get("age")
    gender = persona.get("gender", "")
    background = persona.get("background", "")
    personality = persona.get("personality", "")
    goal = persona.get("goal", "")
    speech_pattern = persona.get("speech_pattern", "")
    emotion_init = persona.get("emotion_init", "")
    emotion_during = persona.get("emotion_during", [])
    emotion_end = persona.get("emotion_end", "")
    voice_tags = persona.get("voice_tags", [])

    return (
        f"- {pid} ({name})\n"
        f"    Role: {role}\n"
        f"    Age/Gender: {age} / {gender}\n"
        f"    Background: {background}\n"
        f"    Personality: {personality}\n"
        f"    Goal: {goal}\n"
        f"    Speech: {speech_pattern}\n"
        f"    Emotions: start={emotion_init}; during={', '.join(emotion_during) or '(không nêu)'}; end={emotion_end}\n"
        f"    Voice tags: {', '.join(voice_tags) or '(không nêu)'}"
    )


def _default_output_path(case_id: str) -> Path:
    safe_case = case_id or "personas"
    return Path(f"{safe_case}_personas.json")


def _persist_output(state: PersonaState, output_path: Path) -> None:
    payload = {
        "case_id": state.get("case_id"),
        "personas": state.get("persona_profiles", []),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)
    print(f"\nĐã lưu persona JSON tại: {output_path}")


def main() -> None:
    graph = build_persona_graph()

    state: PersonaState = {
        "case_json_path": str(Path("data/drown.json").expanduser()),
    }

    state = graph.invoke(state)  # type: ignore[assignment]

    case_id = state.get("case_id", "(unknown)")
    print("Persona profiles generated for case:", case_id)

    personas = state.get("persona_profiles", [])
    _print_section("Personas", (_format_persona(persona) for persona in personas))

    output_path = (
        _default_output_path(str(state.get("case_id", "personas")))
    )
    _persist_output(state, output_path)


if __name__ == "__main__":
    main()
