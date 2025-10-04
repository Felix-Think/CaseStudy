from typing import TypedDict, Dict, Any

class GraphState(TypedDict, total=False):
    raw_user_input: str 
    objective_learning: str
    initial_context: str
    persona: Dict[str, Any]
    generated_scene: str
    
