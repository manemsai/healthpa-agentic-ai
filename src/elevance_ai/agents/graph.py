"""Lightweight orchestration for the local HealthPA agent demo."""

from __future__ import annotations

from dataclasses import dataclass

from elevance_ai.agents.coverage_agent import build_coverage_response
from elevance_ai.agents.policy_agent import PolicyAgent
from elevance_ai.agents.provider_cost_agent import build_provider_cost_response
from elevance_ai.agents.reviewer import review_decision
from elevance_ai.agents.router import route_question
from elevance_ai.domain.evidence import AssistantDecision
from elevance_ai.tools.policy_tools import PolicySearchTool
from elevance_ai.observability.metrics import record_query


@dataclass(slots=True)
class HealthPAGraph:
    """Small deterministic graph facade used by the API, CLI, and tests."""

    policy_tool: PolicySearchTool

    def invoke(
        self,
        question: str,
        *,
        market: str,
        line_of_business: str,
        top_k: int = 5,
    ) -> AssistantDecision:
        """Route a question and return a reviewed decision envelope."""

        route = route_question(question)
        if route == "policy":
            decision = PolicyAgent(self.policy_tool).answer(
                question,
                market=market,
                line_of_business=line_of_business,
                top_k=top_k,
            )
        elif route == "provider_cost":
            decision = build_provider_cost_response(question)
        elif route == "coverage":
            decision = build_coverage_response(question)
        else:
            decision = build_coverage_response(question)
        reviewed = review_decision(decision)
        record_query(route, reviewed.status)
        return reviewed


def build_graph(policy_tool: PolicySearchTool) -> HealthPAGraph:
    """Build the local graph facade."""

    return HealthPAGraph(policy_tool=policy_tool)
