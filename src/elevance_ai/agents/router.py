"""Routing logic for multi-agent workflows."""

from __future__ import annotations

from elevance_ai.agents.state import RouteName

POLICY_TERMS = {
    "policy",
    "prior authorization",
    "preauthorization",
    "medical necessity",
    "covered",
    "coverage",
    "guideline",
    "criteria",
    "procedure",
}
COST_TERMS = {"cost", "price", "rate", "allowed amount", "negotiated", "cpt", "billing code"}
MEMBER_TERMS = {"my plan", "my benefits", "member", "claim", "deductible", "copay", "coinsurance"}


def route_question(question: str) -> RouteName:
    """Route a user question to the best available demo agent."""

    normalized = question.lower()
    if any(term in normalized for term in COST_TERMS):
        return "provider_cost"
    if any(term in normalized for term in MEMBER_TERMS):
        return "coverage"
    if any(term in normalized for term in POLICY_TERMS):
        return "policy"
    return "review"
