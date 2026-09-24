from __future__ import annotations

from typing import TypedDict


class HealthPAState(TypedDict, total=False):

    query: str

    intent: str

    retrieved_results: list[dict]

    selected_sources: list[dict]

    answer: str

    retrieval_confidence: float

    grounding_score: float

    requires_human_review: bool

    final_status: str

    error: str

    evidence_sufficient: bool
    
    review_reason: str