from typing import Dict, Any
from agent.chain.generate_scene import generate_scene

def generate_scene_node(state: Dict[str, Any]) -> Dict[str, Any]:
    input_state = {
        "objective_learning": state.get("objective_learning", ""),
        "initial_context": state.get("initial_context", ""),
        "persona": state.get("persona", {}),
    }
    new_state = generate_scene(input_state)
    return {**state, **new_state}