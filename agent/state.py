from typing import TypedDict, Dict, Any, List


class DialogueEntry(TypedDict, total=False):
    speaker: str
    dialogue: str
    action: str
    emotion: str
    context: str


class GraphState(TypedDict, total=False):
    raw_user_input: str
    Scenario_Name: str
    Learning_Objective: Dict[str, Any]
    Initial_Context: Dict[str, Any]

    Persona: Dict[str, Any]
    Current_Persona: Dict[str, Any]
    Current_Persona_Emotion: str
    Current_Persona_Action: str
    Main_Character_Action: str
    Main_Character_Emotion: str
    Main_Character_Dialogue: str
    Persona_Current: DialogueEntry
    Persona_Dialogue_Log: List[DialogueEntry]

    Main_Current: DialogueEntry
    Main_Dialogue_Log: List[DialogueEntry]

    Scene_Narration: str
    Narrator_Focus: str
    Story_Phase: str
    Narrative_Mode: str
    Persona_Present: bool
    Supervisor_Route: str
