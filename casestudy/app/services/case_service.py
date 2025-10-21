from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

from casestudy.app.core.config import get_settings
from casestudy.app.crud.case_crud import fetch_cases
from casestudy.app.models.case import CaseDocument
from casestudy.app.schemas.case import CaseListResponse, CaseSummary
from casestudy.utils.load import load_case_from_local


class CaseService:
    """
    Tầng dịch vụ tập trung toàn bộ nghiệp vụ cho case:
    - Ưu tiên lấy dữ liệu từ MongoDB.
    - Nếu có lỗi kết nối sẽ fallback về dữ liệu local.
    """

    def __init__(self) -> None:
        self.settings = get_settings()

    def list_cases(self, limit: int = 50) -> CaseListResponse:
        cases, source = self._list_from_mongo(limit)
        if not cases:
            cases, source = self._list_from_local(limit)
        return CaseListResponse(cases=cases, source=source)

    def _list_from_mongo(self, limit: int) -> Tuple[List[CaseSummary], str]:
        try:
            documents = fetch_cases(limit)
        except Exception:
            return [], "local"
        summaries = [self._to_summary(doc) for doc in documents]
        return summaries, "mongo"

    def _list_from_local(self, limit: int) -> Tuple[List[CaseSummary], str]:
        cases_dir: Path = self.settings.case_data_dir
        if not cases_dir.exists():
            return [], "local"

        summaries: List[CaseSummary] = []
        for case_dir in sorted(cases_dir.iterdir()):
            if not case_dir.is_dir():
                continue
            case_id = case_dir.name
            context, _, _ = load_case_from_local(case_id)
            if not context:
                continue
            summaries.append(self._to_summary(CaseDocument.from_dict(context)))
            if len(summaries) >= limit:
                break
        return summaries, "local"

    @staticmethod
    def _to_summary(document: CaseDocument) -> CaseSummary:
        return CaseSummary(
            case_id=document.case_id,
            topic=document.topic,
            summary=document.summary,
            location=document.location,
            time=document.time,
            who_first_on_scene=document.who_first_on_scene,
        )
