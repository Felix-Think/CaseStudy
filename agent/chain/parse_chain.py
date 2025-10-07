from typing import Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from agent.state import GraphState
import os
from dotenv import load_dotenv

load_dotenv()

class PersonaInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    Role: str = ""
    Background: str = ""
    Personality: str = ""
    Notes: str = ""


class ParseInputSchema(BaseModel):
    """Schema chuẩn để parse output JSON từ LLM."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    Scenario_Name: str = Field(..., alias="Scenario Name")
    Learning_Objective: Dict[str, Any] = Field(..., alias="Learning Objective")
    Initial_Context: Dict[str, Any] = Field(..., alias="Initial Context")
    Persona: PersonaInfo = Field(default_factory=PersonaInfo, alias="Persona (Characteristic)")

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
                "Bạn là AI chuyên phân tích và trích xuất dữ liệu case study dành cho mô hình huấn luyện nhập vai. "
                "Nhiệm vụ của bạn: Đọc mô tả đầu vào thô và trích xuất chính xác các phần sau, trả về đúng dạng JSON. "
                "\n\nYÊU CẦU ĐỊNH DẠNG JSON CHUẨN:"
                "\n{{"
                '\n  "Scenario Name": "<Tên kịch bản>",'
                '\n  "Learning Objective": {{'
                '\n    "Learning Objective": "<Mục tiêu học tập chi tiết, mô tả năng lực và hành vi cần đánh giá>"'
                "\n  }},"
                '\n  "Initial Context": {{'
                '\n    "Enter Narrative": "<Bối cảnh mở đầu, mô tả tình huống, thời gian, địa điểm, hành động của nhân vật chính>"'
                "\n  }},"
                '\n  "Persona (Characteristic)": {{'
                '\n    "Role": "<Vai trò của nhân vật phụ (nếu có)>",'
                '\n    "Background": "<Bối cảnh và mối quan hệ giữa nhân vật phụ với nhân vật chính hoặc nạn nhân>",'
                '\n    "Personality": "<Tính cách, cảm xúc và hành vi đặc trưng của nhân vật phụ>",'
                '\n    "Notes": "<Ghi chú đặc biệt, lưu ý khi nhập vai hoặc hạn chế cần tuân thủ>"'
                "\n  }},"
                "\n}}"
                "\n\nHƯỚNG DẪN:"
                "\n- Không thêm markdown, không giải thích, không dịch. "
                "\n- Nếu thông tin thiếu, để chuỗi rỗng hoặc mô tả ngắn gọn. "
                "\n- Phải giữ nguyên cấu trúc và tên khóa (keys) như trên, bao gồm dấu hoa, dấu ngoặc và dấu hai chấm chính xác. "
                "\n- Chỉ điền dữ liệu nhân vật phụ trong Persona (Characteristic). Nếu đầu vào chỉ nhắc nhân vật chính, hãy trả về rỗng phần Persona. Không suy diễn."
                "\n- Nội dung phải viết bằng tiếng Việt tự nhiên, phù hợp với ngữ cảnh đào tạo nhập vai chuyên nghiệp."
            ),
            ("human", "{raw_user_input}"),
        ]
    ).partial(format_instructions=format_instructions)
)



# ------------------- TOOL -------------------
@tool("parse_input_tool", return_direct=True)
def parse_input_tool(raw_user_input: str) -> Dict[str, Any]:
    """
    Mô tả:
        Công cụ này dùng để phân tích và trích xuất dữ liệu có cấu trúc từ phần mô tả thô
        mà người hướng dẫn (hoặc người thiết kế case study) cung cấp.

    Chức năng:
        - Nhận vào một đoạn mô tả tình huống huấn luyện (bằng tiếng Việt hoặc tiếng Anh).
        - Sử dụng mô hình ngôn ngữ để tự động nhận diện và trích xuất các phần chính:
            1. **Scenario Name** – tên kịch bản học tập.
            2. **Learning Objective** – mục tiêu học tập chi tiết, mô tả năng lực cần đánh giá.
            3. **Initial Context** – bối cảnh mở đầu của tình huống (thời gian, địa điểm, nhân vật chính, sự kiện khởi đầu).
            4. **Persona (Characteristic)** – chỉ ghi thông tin nhân vật phụ (vai trò, hoàn cảnh, tính cách, ghi chú). Nếu không có nhân vật phụ, trả về các chuỗi rỗng.
 
        
    Định dạng đầu ra:
        Trả về một `dict` (từ điển Python) theo đúng cấu trúc JSON chuẩn:
        {
            "Scenario Name": "<Tên kịch bản>",
            "Learning Objective": { "Learning Objective": phụ"<Mục tiêu học tập>" },
            "Initial Context": { "Enter Narrative": "<Bối cảnh mở đầu>" },
            "Persona (Characteristic)": {
                "Role": "<Vai trò>",
                "Background": "<Bối cảnh và mối quan hệ>",
                "Personality": "<Tính cách và cảm xúc>",
                "Notes": "<Ghi chú đặc biệt>"
            },
        }

    Tham số:
        raw_user_input (str):
            Đoạn mô tả thô do người thiết kế cung cấp — có thể chứa bối cảnh, mục tiêu học tập, nhân vật phụ, v.v.

    Giá trị trả về:
        Dict[str, Any]:
            Một đối tượng từ điển chứa các trường được trích xuất theo format JSON ở trên.
            Có thể được parse trực tiếp sang Pydantic model hoặc lưu thành GraphState.

    Ví dụ:
        >>> parse_input_tool("Tình huống: Một bé trai bị đuối nước tại hồ bơi, bác sĩ cấp cứu vừa đến hiện trường...")
        {
            "Scenario Name": "Cấp cứu đuối nước tại hồ bơi",
            "Learning Objective": {...},
            "Initial Context": {...},
            "Persona (Characteristic)": {...}
        }
    """
    chain = parse_prompt | llm | parser
    result = chain.invoke({"raw_user_input": raw_user_input})
    return result.model_dump(by_alias=True)
