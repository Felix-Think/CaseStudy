from __future__ import annotations

from typing import Any, Dict, Iterable, List

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable

from ..const import DEFAULT_CASE_ID


def create_persona_digest_chain(
    persona_index,
    llm,
    *,
    case_id: str = DEFAULT_CASE_ID,
    top_k: int = 2,
) -> Runnable:
    """
    Build a chain that consolidates persona details into short operational digests.
    The prompt avoids assumptions about persona structure so it can adapt to
    future case studies.
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "Bạn đang chuẩn bị thông tin nhân vật cho một mô phỏng học viên. "
                    "Giữ giọng điệu trung lập, tập trung vào mục tiêu, hành vi và trạng thái cảm xúc."
                ),
            ),
            (
                "human",
                (
                    "Case ID: {case_id}\n"
                    "Danh sách mô tả nhân vật thu thập được:\n{documents}\n\n"
                    "Yêu cầu: Với mỗi persona_id, hãy tóm tắt 2 câu gồm:\n"
                    "- Bối cảnh/nghề nghiệp, mục tiêu chính đối với mô phỏng.\n"
                    "- Trạng thái cảm xúc ban đầu hoặc dấu hiệu hành vi quan trọng.\n"
                    "Định dạng:\n"
                    "- {{persona_id}}: <tóm tắt>. Cảm xúc: <emotion>."
                ),
            ),
        ]
    )
    chain = prompt | llm | StrOutputParser()

    def build_digest(payload: Dict[str, Any]) -> str:
        persona_ids: Iterable[str] = payload.get("persona_ids", [])
        documents: List[str] = []

        for persona_id in persona_ids:
            query = payload.get(
                "query_template",
                "Thông tin nhân vật {persona_id} trong mô phỏng",
            ).format(persona_id=persona_id)
            results = persona_index.similarity_search(query, k=top_k)
            if not results:
                documents.append(f"[{persona_id}] Không tìm thấy dữ liệu nhân vật.")
            else:
                for doc in results:
                    documents.append(
                        f"[{doc.metadata.get('persona_id', persona_id)}] {doc.page_content}"
                    )

        formatted_docs = "\n".join(documents) or "Không có dữ liệu nhân vật."
        return chain.invoke({"case_id": case_id, "documents": formatted_docs})

    return build_digest
