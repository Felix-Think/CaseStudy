from typing import TypedDict, List, Dict, Any, NotRequired

class SkeletonState(TypedDict, total=False):
    """State container for skeleton generation pipeline."""

    # Đường dẫn hoặc nội dung JSON của case study
    case_json_path: str
    case_data: Dict[str, Any]

    # Thông tin meta
    case_id: str
    language: str
    topic: str

    # Bối cảnh ban đầu (cảnh, nguồn lực, ràng buộc)
    initial_context: Dict[str, Any]

    # Mục tiêu học tập (mỗi mục tiêu có id, title, description, success_criteria)
    learning_objectives: List[Dict[str, Any]]

    # Danh sách persona trong kịch bản (không bao gồm learner)
    personas: List[Dict[str, Any]]

    # (Tùy chọn) – nơi để hệ thống sinh ra dàn khung sự kiện (canon events)
    canon_events: NotRequired[List[Dict[str, Any]]]