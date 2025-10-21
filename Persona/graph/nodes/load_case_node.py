"""Node that loads the raw case JSON for persona generation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from Persona.state import PersonaState

DEFAULT_CASE_PATH = "data/drown.json"


def load_case_node(state: PersonaState) -> PersonaState:
    """Load case study JSON from disk (or a state override)."""
    source_path = state.get("case_json_path") or str(DEFAULT_CASE_PATH)
    path = Path(source_path).expanduser().resolve()

    try:
        with path.open(encoding="utf-8") as file:
            data: Dict[str, Any] = json.load(file)
    except FileNotFoundError as exc:  # pragma: no cover - defensive guard
        raise RuntimeError(f"Không tìm thấy file case JSON tại {path}") from exc

    return {
        **state,
        "case_json_path": str(path),
        "case_data": data,
        "case_id": data.get("case_id", ""),
        "language": data.get("language", ""),
        "topic": data.get("topic", ""),
        "initial_context": data.get("initial_context", {}),
        "personas": data.get("personas", []),
    }

