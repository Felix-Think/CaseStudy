from typing import Dict, Any
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from agent.state import GraphState
import os
from dotenv import load_dotenv

load_dotenv()

class ParseInputSchema(BaseModel):
    objective_learning: str
    initial_context: str
    persona: Dict[str, Any]

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.2,
    api_key=os.getenv("OPENAI_API_KEY")
)


parser = PydanticOutputParser(pydantic_object=ParseInputSchema)
format_instructions = parser.get_format_instructions()

parse_prompt = (
    ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Bạn là AI chuyên phân tích yêu cầu xây dựng case study. "
                "Nhiệm vụ của bạn: (1) xác định mục tiêu học tập người dạy cung cấp, "
                "(2) nêu bối cảnh mở đầu của tình huống, (3) trích xuất thông tin nhân vật. "
                "Trả về JSON đúng với schema:\n{format_instructions}\n"
                "TIÊU CHÍ:\n"
                "- objective_learning: mô tả rõ kết quả học tập.\n"
                "- initial_context: tóm tắt bối cảnh xuất phát, trạng thái ban đầu.\n"
                "- persona: object chứa name, role, traits (list), speaking_style."
                " Nếu thiếu dữ liệu, trả chuỗi rỗng hoặc danh sách rỗng.\n"
                "KHÔNG dịch nội dung; KHÔNG thêm giải thích hay markdown. "
                "Viết đúng JSON, không phẩy thừa.",
            ),
            ("human", "{raw_user_input}"),
        ]
    ).partial(format_instructions=format_instructions)
)


# ------------------- TOOL -------------------
@tool("parse_input_tool", return_direct=True)
def parse_input_tool(raw_user_input: str) -> Dict[str, Any]:
    """
    Trích xuất dữ liệu có cấu trúc từ đầu vào thô của người hướng dẫn.
    Output gồm:
    - objective_learning
    - initial_context
    - persona
    """
    chain = parse_prompt | llm | parser
    result = chain.invoke({"raw_user_input": raw_user_input})
    return result.dict()