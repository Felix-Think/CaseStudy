from typing import TypedDict, Dict, Any

class GraphState(TypedDict, total=False):
    raw_user_input: str
    Scenario_Name: str
    Learning_Objective: Dict[str, Any]
    Initial_Context: Dict[str, Any]
    Persona: Dict[str, Any]
    Current_Persona_Emotion: str
    Current_Persona_Action: str