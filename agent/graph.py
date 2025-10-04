
from typing import TypedDict, Dict, Any
import json
from dotenv import load_dotenv
import os
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END

from agent.state import GraphState
from agent.nodes.parse_input import parse_input_node
from agent.nodes.generator_node import generate_scene_node

load_dotenv()

graph = StateGraph(GraphState)
graph.add_node("parse_input", parse_input_node)
graph.add_node("generate_scene", generate_scene_node)

graph.set_entry_point("parse_input")
graph.add_edge("parse_input", "generate_scene")
graph.add_edge("generate_scene", END)

app = graph.compile()

if __name__ == "__main__":
    test_input = """
    Mục tiêu học tập: Hiểu và áp dụng các khái niệm cơ bản về lập trình Python.
    Bối cảnh mở đầu: Học sinh đã có kiến thức cơ bản về lập trình.
    Nhân vật: Một giáo viên nhiệt huyết, kiên nhẫn, luôn khuyến khích học sinh.
    """
    result = app.invoke({"raw_user_input": test_input})
    print("🎯 Objective:", result["objective_learning"])
    print("📖 Context:", result["initial_context"])
    print("🧑 Persona:", result["persona"])
    print("🎬 Scene:", result["generated_scene"])
