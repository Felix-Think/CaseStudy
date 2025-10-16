from __future__ import annotations

from typing import Any, Dict, List

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable

from ..const import DEFAULT_CASE_ID


def create_responder_chain(
    llm,
    *,
    case_id: str = DEFAULT_CASE_ID,
) -> Runnable:
    """
    Generate facilitator-style feedback for the trainee using the consolidated state.
    The prompt emphasises coaching language that should transfer across case studies.
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "Bạn là AI facilitator hỗ trợ học viên trong mô phỏng tình huống y khoa. "
                    "Hãy phản hồi súc tích, hướng dẫn tiếp theo và giữ thái độ hỗ trợ."
                ),
            ),
            (
                "human",
                (
                    "Case ID: {case_id}\n"
                    "Canon Event: {event_title}\n"
                    "Tóm tắt bối cảnh: {scene_summary}\n"
                    "Yêu cầu hành động: {required_actions}\n"
                    "Nhân vật đang hiện diện: {persona_overview}\n"
                    "Lịch sử hội thoại: {dialogue_history}\n"
                    "Vi phạm hoặc lưu ý policy: {policy_flags}\n"
                    "Hành động gần nhất của học viên: {user_action}\n\n"
                    "Hãy trả lời tối đa 4 câu tiếng Việt:\n"
                    "1. Nhận xét nhanh về tình hình hiện tại.\n"
                    "2. Đánh giá hành động học viên (nếu có) dựa trên yêu cầu.\n"
                    "3. Gợi ý bước tiếp theo cụ thể.\n"
                    "4. Nhắc nhở an toàn hoặc policy nếu cần."
                ),
            ),
        ]
    )
    chain = prompt | llm | StrOutputParser()

    def respond(payload: Dict[str, Any]) -> str:
        dialogue_history: List[Dict[str, str]] = payload.get("dialogue_history", [])
        history_text = "\n".join(
            f"{turn.get('speaker', 'unknown')}: {turn.get('content', '')}"
            for turn in dialogue_history
        ) or "Chưa có hội thoại."

        policy_flags = payload.get("policy_flags")
        if isinstance(policy_flags, list) and policy_flags:
            policy_text = "; ".join(flag.get("policy_text", "") for flag in policy_flags)
        else:
            policy_text = "Không có."

        return chain.invoke(
            {
                "case_id": case_id,
                "event_title": payload.get("event_title", "Sự kiện"),
                "scene_summary": payload.get("scene_summary", "Chưa có dữ liệu."),
                "required_actions": payload.get("required_actions", []),
                "persona_overview": payload.get("persona_overview", "Không có."),
                "dialogue_history": history_text,
                "policy_flags": policy_text,
                "user_action": payload.get("user_action", "Chưa ghi nhận."),
            }
        )

    return respond
