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
                    "Số lượt đã dùng: {turn_count}\n"
                    "Giới hạn lượt: {max_turns}\n"
                    "Thông báo hệ thống: {system_notice}\n"
                    "Hành động gần nhất của học viên: {user_action}\n\n"
                    "Nếu có thông báo hệ thống, hãy ghi nhận rõ tình trạng và hướng dẫn cách bắt đầu lại.\n"
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

        required_actions = payload.get("required_actions", [])
        if isinstance(required_actions, list):
            required_actions_text = "; ".join(required_actions) or "Không có."
        else:
            required_actions_text = required_actions or "Không có."

        policy_flags = payload.get("policy_flags")
        if isinstance(policy_flags, list) and policy_flags:
            policy_text = "; ".join(flag.get("policy_text", "") for flag in policy_flags)
        else:
            policy_text = "Không có."

        max_turns_value = payload.get("max_turns")
        if isinstance(max_turns_value, int) and max_turns_value > 0:
            max_turns_text = str(max_turns_value)
        elif isinstance(max_turns_value, str) and max_turns_value:
            max_turns_text = max_turns_value
        else:
            max_turns_text = "Không giới hạn"

        turn_count = payload.get("turn_count", 0)
        system_notice = payload.get("system_notice") or "Không có."

        return chain.invoke(
            {
                "case_id": case_id,
                "event_title": payload.get("event_title", "Sự kiện"),
                "scene_summary": payload.get("scene_summary", "Chưa có dữ liệu."),
                "required_actions": required_actions_text,
                "persona_overview": payload.get("persona_overview", "Không có."),
                "dialogue_history": history_text,
                "policy_flags": policy_text,
                "user_action": payload.get("user_action", "Chưa ghi nhận."),
                "turn_count": turn_count,
                "max_turns": max_turns_text,
                "system_notice": system_notice,
            }
        )

    return respond
