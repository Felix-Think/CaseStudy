from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Tuple

from casestudy.app.core.config import get_settings
from casestudy.app.crud.case_crud import fetch_cases, upsert_case_documents
from casestudy.app.models.case import CaseDocument
from casestudy.app.schemas.case import (
    CaseCreatePayload,
    CaseCreateResponse,
    CaseListResponse,
    CaseSummary,
)
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

    def create_case(
        self,
        payload: CaseCreatePayload,
        *,
        persist_local: bool = True,
    ) -> CaseCreateResponse:
        case_id = self._resolve_case_id(payload)
        context = self._prepare_context(case_id, payload.context)
        personas = self._prepare_personas(case_id, payload.personas)
        skeleton = self._prepare_skeleton(case_id, payload.skeleton)

        try:
            personas_count, _ = upsert_case_documents(
                case_id=case_id,
                context=context,
                personas=personas,
                skeleton=skeleton,
            )
        except RuntimeError as exc:
            raise RuntimeError("Không thể kết nối MongoDB để lưu case.") from exc
        except Exception as exc:  # pragma: no cover - phòng xa lỗi PyMongo
            raise RuntimeError("Lỗi ghi dữ liệu case vào MongoDB.") from exc

        local_path = None
        if persist_local:
            local_path = self._write_local_case(case_id, context, personas, skeleton)

        return CaseCreateResponse(
            case_id=case_id,
            personas_count=personas_count,
            message=f"Đã lưu case '{case_id}' lên MongoDB.",
            local_path=str(local_path) if local_path else None,
        )

    @staticmethod
    def _resolve_case_id(payload: CaseCreatePayload) -> str:
        candidates = [
            payload.case_id,
            payload.context.get("case_id") if isinstance(payload.context, dict) else None,
        ]

        skeleton = payload.skeleton
        if isinstance(skeleton, dict):
            candidates.append(skeleton.get("case_id"))

        personas = payload.personas
        if isinstance(personas, dict):
            candidates.append(personas.get("case_id"))

        for candidate in candidates:
            if candidate:
                return str(candidate)

        raise ValueError("Thiếu case_id trong payload.")

    @staticmethod
    def _prepare_context(case_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        data = deepcopy(context)
        data.pop("_id", None)
        data["case_id"] = case_id
        return data

    @staticmethod
    def _prepare_personas(
        case_id: str, personas_payload: Any
    ) -> List[Dict[str, Any]]:
        if isinstance(personas_payload, dict):
            personas_raw = personas_payload.get("personas", [])
        else:
            personas_raw = personas_payload

        if not isinstance(personas_raw, list):
            raise ValueError("Dữ liệu personas phải là danh sách.")

        personas: List[Dict[str, Any]] = []
        for persona in personas_raw:
            if not isinstance(persona, dict):
                raise ValueError("Mỗi persona phải là object.")
            item = deepcopy(persona)
            item.pop("_id", None)
            item["case_id"] = case_id
            personas.append(item)
        return personas

    @staticmethod
    def _prepare_skeleton(case_id: str, skeleton: Dict[str, Any]) -> Dict[str, Any]:
        data = deepcopy(skeleton)
        data.pop("_id", None)
        data["case_id"] = case_id
        return data

    def _write_local_case(
        self,
        case_id: str,
        context: Dict[str, Any],
        personas: List[Dict[str, Any]],
        skeleton: Dict[str, Any],
    ) -> Path:
        base_dir = self.settings.case_data_dir / case_id
        base_dir.mkdir(parents=True, exist_ok=True)

        with (base_dir / "context.json").open("w", encoding="utf-8") as f:
            json.dump(context, f, ensure_ascii=False, indent=2)

        with (base_dir / "personas.json").open("w", encoding="utf-8") as f:
            json.dump(
                {"case_id": case_id, "personas": personas},
                f,
                ensure_ascii=False,
                indent=2,
            )

        with (base_dir / "skeleton.json").open("w", encoding="utf-8") as f:
            json.dump(skeleton, f, ensure_ascii=False, indent=2)

        return base_dir
