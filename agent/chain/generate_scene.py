import json
from typing import Any, Dict
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()
from agent.state import GraphState


class ScenePlan(BaseModel):
    objective_learning: str = Field(..., description="Mục tiêu học tập gốc")
    initial_context: str = Field(..., description="Bối cảnh ban đầu và vai trò nhân vật chính")
    persona: Dict[str, Any] = Field(default_factory=dict, description="Thông tin nhân vật của casestudy")
    generated_scene: str = Field(
        ...,
        description="Tình huống học tập chi tiết, có xung đột và thách thức liên quan mục tiêu",
    )


scene_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Bạn là AI chuyên tạo tình huống học tập dựa trên mục tiêu và bối cảnh. "
            "Nhiệm vụ của bạn: (1) tạo chuỗi sự kiện chi tiết, "
            "(2) phát triển nhân vật nếu trong yêu cầu của người hướng dẫn có yêu cầu, "
            "(3) xây dựng xung đột và thách thức gắn với mục tiêu học tập, "
            "và (4) trình bày trọn vẹn tình huống trong trường generated_scene. "
            "\nYêu cầu:\n"
            "- Tình huống phải có khai mở, cao trào và thử thách cụ thể.\n"
            "- Thể hiện vai trò của nhân vật chính và mối liên hệ với mục tiêu học tập.\n"
            "- Trả về JSON đúng schema:\n"
            "{format_instructions}\n"
            "KHÔNG dịch nội dung; KHÔNG thêm giải thích hay markdown. "
            "Viết đúng JSON, không phẩy thừa.",
        ),
        (
            "human",
            "Dựa trên mục tiêu học tập: {objective_learning}, bối cảnh: {initial_context}, "
            "và nhân vật chính: {persona}, hãy tạo tình huống học tập chi tiết.",
        ),
    ]
)

parser = PydanticOutputParser(pydantic_object=ScenePlan)
scene_prompt = scene_prompt.partial(format_instructions=parser.get_format_instructions())

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)


def generate_scene(state: GraphState) -> GraphState:
    objective = state.get("objective_learning", "")
    context = state.get("initial_context", "")
    persona = state.get("persona", {}) or {}

    chain = scene_prompt | llm | parser
    result = chain.invoke(
        {
            "objective_learning": objective,
            "initial_context": context,
            "persona": json.dumps(persona, ensure_ascii=False),
        }
    )

    state["generated_scene"] = result.generated_scene
    return state
