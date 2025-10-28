from __future__ import annotations

from typing import Any, Dict, List, Tuple

from pymongo.collection import Collection

from casestudy.app.core.config import get_settings
from casestudy.app.db.database import get_mongo_client
from casestudy.app.models.case import CaseDocument


def _get_context_collection() -> Collection:
    client = get_mongo_client()
    if client is None:
        raise RuntimeError("MongoDB client chưa sẵn sàng.")
    settings = get_settings()
    return client[settings.mongo_db].contexts


def _get_persona_collection() -> Collection:
    client = get_mongo_client()
    if client is None:
        raise RuntimeError("MongoDB client chưa sẵn sàng.")
    settings = get_settings()
    return client[settings.mongo_db].personas


def _get_skeleton_collection() -> Collection:
    client = get_mongo_client()
    if client is None:
        raise RuntimeError("MongoDB client chưa sẵn sàng.")
    settings = get_settings()
    return client[settings.mongo_db].skeletons


def fetch_cases(limit: int) -> List[CaseDocument]:
    """
    Lấy danh sách case từ MongoDB, giới hạn theo tham số limit.
    """
    collection = _get_context_collection()
    cursor = (
        collection.find({}, {"_id": 0})
        .sort("case_id", 1)
        .limit(limit)
    )
    return [CaseDocument.from_dict(doc) for doc in cursor]


def upsert_case_documents(
    case_id: str,
    context: Dict[str, Any],
    personas: List[Dict[str, Any]],
    skeleton: Dict[str, Any],
) -> Tuple[int, int]:
    """
    Ghi đè dữ liệu case trong MongoDB theo case_id.
    Trả về tuple (personas_count, skeleton_count)
    """
    context_col = _get_context_collection()
    persona_col = _get_persona_collection()
    skeleton_col = _get_skeleton_collection()

    context_col.delete_many({"case_id": case_id})
    persona_col.delete_many({"case_id": case_id})
    skeleton_col.delete_many({"case_id": case_id})

    context_col.insert_one(context)
    inserted_personas = 0
    if personas:
        persona_col.insert_many(personas)
        inserted_personas = len(personas)

    skeleton_col.insert_one(skeleton)

    return inserted_personas, 1
