from __future__ import annotations

from typing import List

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
