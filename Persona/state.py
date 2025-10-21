from typing import Dict, List, Any, NotRequired, TypedDict


class PersonaState(TypedDict, total=False):
    """State container for persona generation pipeline."""

    case_json_path: str
    case_data: Dict[str, Any]

    case_id: str
    language: str
    topic: str

    initial_context: Dict[str, Any]
    personas: List[Dict[str, Any]]

    persona_profiles: NotRequired[List[Dict[str, Any]]]

