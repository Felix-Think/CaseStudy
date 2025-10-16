from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class PersonaState(BaseModel):
    id: str
    name: str
    role: str
    emotion: str = "neutral"
    trust: float = 0.5

class RuntimeState(BaseModel):
    case_id: str
    current_event: str
    scene_summary: Optional[str] = None
    active_personas: Dict[str, PersonaState] = Field(default_factory=dict) 
    dialogue_history: List[Dict[str, str]] = Field(default_factory=list)
    user_action: Optional[str] = None
    event_summary: Dict[str, str] = Field(default_factory=dict)  # CE1, CE2...: pass/fail
    policy_flags: List[Dict[str, str]] = Field(default_factory=list)
