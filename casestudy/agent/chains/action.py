from __future__ import annotations

import re
import unicodedata
from typing import Any, Dict, List

from langchain_core.runnables import Runnable


def _strip_accents(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")


def _normalize(text: str) -> List[str]:
    ascii_text = _strip_accents(text.lower())
    cleaned = re.sub(r"[^a-z0-9\s]", " ", ascii_text)
    return [token for token in cleaned.split() if token]


def _score_match(user_tokens: List[str], requirement: str) -> float:
    requirement_tokens = _normalize(requirement)
    if not requirement_tokens:
        return 0.0

    overlaps = sum(1 for token in requirement_tokens if token in user_tokens)
    if not overlaps:
        return 0.0

    coverage_requirement = overlaps / len(requirement_tokens)
    coverage_user = overlaps / max(1, len(user_tokens))
    return max(coverage_requirement, coverage_user)


def create_action_evaluator_chain(
    *,
    pass_threshold: float = 0.55,
    attention_threshold: float = 0.35,
) -> Runnable:
    """
    Simple keyword-overlap evaluator that is deterministic and does not rely on LLM.
    Tunable thresholds let us adapt to different case studies without rewriting code.
    """

    def evaluate(payload: Dict[str, Any]) -> Dict[str, Any]:
        user_action = (payload.get("user_action") or "").strip()
        required_actions: List[str] = payload.get("required_actions", [])

        if not user_action or not required_actions:
            return {"status": "pending", "matched_actions": [], "scores": []}

        user_tokens = _normalize(user_action)
        scored_matches = [
            (requirement, _score_match(user_tokens, requirement))
            for requirement in required_actions
        ]

        matched_actions = [
            requirement for requirement, score in scored_matches if score >= attention_threshold
        ]
        max_score = max((score for _, score in scored_matches), default=0.0)

        if max_score >= pass_threshold and len(matched_actions) >= max(1, len(required_actions) // 2):
            status = "pass"
        elif matched_actions:
            status = "needs_attention"
        else:
            status = "fail"

        return {
            "status": status,
            "matched_actions": matched_actions,
            "scores": scored_matches,
        }

    return evaluate
