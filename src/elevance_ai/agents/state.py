"""Shared agent state definitions."""

from typing import Literal, TypedDict

from elevance_ai.domain import AssistantDecision, Evidence

RouteName = Literal["policy", "coverage", "provider_cost", "review"]


class AgentState(TypedDict, total=False):
    """Shared state passed through the orchestration graph."""

    question: str
    market: str
    line_of_business: str
    route: RouteName
    retrieved_evidence: list[Evidence]
    warnings: list[str]
    draft_decision: AssistantDecision
