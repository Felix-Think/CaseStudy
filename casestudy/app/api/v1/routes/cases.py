from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from casestudy.app.dependencies.cases import get_case_service
from casestudy.app.schemas.case import CaseListResponse
from casestudy.app.services.case_service import CaseService

router = APIRouter(prefix="/cases", tags=["cases"])


@router.get("/", response_model=CaseListResponse)
async def list_cases_endpoint(
    limit: int = Query(50, ge=1, le=200),
    service: CaseService = Depends(get_case_service),
) -> CaseListResponse:
    return service.list_cases(limit=limit)
