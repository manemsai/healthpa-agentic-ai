"""Provider cost agent implementation."""

from __future__ import annotations

from elevance_ai.domain.evidence import AssistantDecision


def build_provider_cost_response(question: str) -> AssistantDecision:
    """Return a conservative response for price-transparency questions."""

    return AssistantDecision(
        status="human_review_required",
        summary=(
            "The current local demo does not include negotiated-rate files. "
            "Provider cost questions should be answered only after loading validated rate data."
        ),
        prior_auth_status="unknown",
        confidence=0.3,
        warnings=[
            "Public price-transparency data can be large, delayed, and not member-specific.",
            "Actual out-of-pocket cost depends on plan design, eligibility, and claim adjudication.",
        ],
        recommended_next_steps=[
            "Load machine-readable rate data into the pricing index.",
            "Verify member benefits before estimating out-of-pocket cost.",
        ],
    )
