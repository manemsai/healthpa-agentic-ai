"""Coverage-focused agent implementation."""

from __future__ import annotations

from elevance_ai.domain.evidence import AssistantDecision


def build_coverage_response(question: str) -> AssistantDecision:
    """Return a safe response for member-specific coverage questions."""

    return AssistantDecision(
        status="human_review_required",
        summary=(
            "This question appears to require member-specific benefit, claim, or plan details. "
            "Public policy evidence alone is not enough for a final coverage answer."
        ),
        prior_auth_status="plan_verification_required",
        confidence=0.35,
        warnings=[
            "Do not use this proof of concept to approve, deny, or quote member-specific benefits.",
            "Plan documents and authorized eligibility systems must be checked.",
        ],
        recommended_next_steps=[
            "Collect plan, member, provider, diagnosis, and procedure details through approved systems.",
            "Escalate to an authorized benefits or utilization-management workflow.",
        ],
    )
