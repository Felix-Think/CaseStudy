from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


class CaseSummary(BaseModel):
    case_id: str
    topic: Optional[str] = None
    summary: Optional[str] = None
    location: Optional[str] = None
    time: Optional[str] = None
    who_first_on_scene: Optional[str] = None


class CaseListResponse(BaseModel):
    cases: List[CaseSummary]
    source: str
