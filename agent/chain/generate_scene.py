import json
from typing import Any, Dict, List
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from dotenv import load_dotenv
load_dotenv()
from agent.state import GraphState


class SupportingCharacter(BaseModel):
    name: str = Field(..., description="Tên nhân vật phụ")
    role: str = Field(..., description="Vai trò trong tình huống")
    traits: List[str] = Field(default_factory=list, description="Các đặc điểm nổi bật")
    speaking_style: str = Field(..., description="Phong cách giao tiếp")
    contribution: str = Field(..., description="Cách nhân vật thúc đẩy mục tiêu học tập")


class ScenarioEvent(BaseModel):
    order: int = Field(..., ge=1, le=5, description="Thứ tự sự kiện")
    description: str = Field(..., description="Diễn biến chi tiết")
    involved_characters: List[str] = Field(default_factory=list, description="Các nhân vật tham gia")
    conflict_trigger: str = Field(..., description="Điểm xung đột hoặc thách thức")
    objective_alignment: str = Field(..., description="Liên hệ với mục tiêu học tập")


class ScenePlan(BaseModel):
    objective_learning: str = Field(..., description="Mục tiêu học tập gốc")
    initial_context: str = Field(..., description="Bối cảnh ban đầu")
    protagonist: Dict[str, Any] = Field(default_factory=dict, description="Thông tin nhân vật chính")
    supporting_characters: List[SupportingCharacter] = Field(default_factory=list, description="Nhân vật phụ")
    scenario_events: List[ScenarioEvent] = Field(default_factory=list, description="Chuỗi sự kiện chính")
    key_conflicts: List[str] = Field(default_factory=list, description="Các xung đột trung tâm")
    resolution_hook: str = Field(..., description="Hướng mở cho người học giải quyết")


scene_prompt = (
    ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Bạn là AI chuyên tạo tình huống học tập dựa trên mục tiêu và bối cảnh. "
                "Nhiệm vụ của bạn: (1) tạo chuỗi sự kiện chi tiết, "
                "(2) phát triển nhân vật phụ, "
                "(3) xây dựng xung đột và thách thức. "
                "\nYêu cầu:\n"
                "- Tạo 3-5 sự kiện chính, mỗi sự kiện gồm mô tả chi tiết và vai trò nhân vật.\n"
                "- Phát triển 2-3 nhân vật phụ với tên, vai trò, đặc điểm, phong cách nói.\n"
                "- Xây dựng xung đột liên quan đến mục tiêu học tập.\n"
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

    state["generated_scene"] = json.dumps(result.dict(), ensure_ascii=False, indent=2)
    return state
