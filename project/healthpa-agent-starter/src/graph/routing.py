from __future__ import annotations

from src.graph.state import HealthPAState


def route_after_router(
    state: HealthPAState,
) -> str:

    intent = state.get(
        "intent"
    )

    if intent == "coverage":
        return "retrieve"

    return "unsupported"


def route_after_review(
    state: HealthPAState,
) -> str:

    if state.get(
        "requires_human_review",
        False,
    ):
        return "human_review"

    return "final_response"