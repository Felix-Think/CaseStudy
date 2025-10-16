from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

class PersonaState(BaseModel):
    id: str
    name: str
    role: str
    emotion: str = "neutral"
    trust: float = 0.5
    profile: Optional[str] = None

class RuntimeState(BaseModel):
    case_id: str
    current_event: str
    scene_summary: Optional[str] = None
    active_personas: Dict[str, PersonaState] = Field(default_factory=dict) 
    dialogue_history: List[Dict[str, str]] = Field(default_factory=list)
    user_action: Optional[str] = None
    event_summary: Dict[str, Any] = Field(default_factory=dict)  # CE1, CE2...: pass/fail
    policy_flags: List[Dict[str, str]] = Field(default_factory=list)
    ai_reply: Optional[str] = None

    def to_serializable(self) -> Dict[str, Any]:
        data = self.model_dump()
        data["active_personas"] = {
            persona_id: persona.model_dump()
            for persona_id, persona in self.active_personas.items()
        }
        return data

    @classmethod
    def from_serialized(cls, payload: Dict[str, Any]) -> "RuntimeState":
        payload = dict(payload)
        active_personas = payload.get("active_personas", {})
        normalized_personas: Dict[str, PersonaState] = {}
        for persona_id, persona_payload in active_personas.items():
            if isinstance(persona_payload, PersonaState):
                normalized_personas[persona_id] = persona_payload
            else:
                normalized_personas[persona_id] = PersonaState(**persona_payload)
        payload["active_personas"] = normalized_personas
        return cls(**payload)
