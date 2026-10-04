"""Reviewer agent for answer validation."""

from __future__ import annotations

from elevance_ai.domain.evidence import AssistantDecision

FINAL_DECISION_WORDS = {"approved", "denied", "guaranteed", "covered for this member"}


def review_decision(decision: AssistantDecision) -> AssistantDecision:
    """Add safety warnings when a draft answer sounds like a final determination."""

    summary = decision.summary.lower()
    unsafe_words = sorted(word for word in FINAL_DECISION_WORDS if word in summary)
    if not unsafe_words:
        return decision

    warnings = [
        *decision.warnings,
        "Reviewer flagged language that could be read as a final coverage or authorization decision.",
    ]
    next_steps = [
        *decision.recommended_next_steps,
        "Rewrite the answer as evidence guidance and require authorized plan verification.",
    ]
    return decision.model_copy(
        update={
            "status": "human_review_required",
            "prior_auth_status": "plan_verification_required",
            "confidence": min(decision.confidence, 0.4),
            "warnings": warnings,
            "recommended_next_steps": next_steps,
        }
    )
