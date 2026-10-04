"""LangGraph orchestration for the local HealthPA agent demo."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from langgraph.graph import END, START, StateGraph

from elevance_ai.agents.coverage_agent import build_coverage_response
from elevance_ai.agents.policy_agent import PolicyAgent
from elevance_ai.agents.provider_cost_agent import build_provider_cost_response
from elevance_ai.agents.reviewer import review_decision
from elevance_ai.agents.router import route_question
from elevance_ai.agents.state import AgentState
from elevance_ai.domain.evidence import AssistantDecision
from elevance_ai.observability.metrics import record_query
from elevance_ai.tools.policy_tools import PolicySearchTool


@dataclass(slots=True)
class HealthPAGraph:
    """Compiled LangGraph facade used by the API, CLI, and tests."""

    policy_tool: PolicySearchTool
    pricing_path: str | Path | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "_compiled", self._build().compile())

    def _build(self) -> StateGraph:
        graph = StateGraph(AgentState)
        graph.add_node("route", self._route)
        graph.add_node("policy", self._policy)
        graph.add_node("coverage", self._coverage)
        graph.add_node("provider_cost", self._provider_cost)
        graph.add_node("review", self._review)
        graph.add_node("finalize", self._finalize)
        graph.add_edge(START, "route")
        graph.add_conditional_edges("route", lambda state: state["route"], {"policy": "policy", "coverage": "coverage", "provider_cost": "provider_cost", "review": "coverage"})
        graph.add_edge("policy", "review")
        graph.add_edge("coverage", "review")
        graph.add_edge("provider_cost", "review")
        graph.add_edge("review", "finalize")
        graph.add_edge("finalize", END)
        return graph

    def _route(self, state: AgentState) -> AgentState:
        return {"route": route_question(state["question"])}

    def _policy(self, state: AgentState) -> AgentState:
        decision = PolicyAgent(self.policy_tool).answer(state["question"], market=state["market"], line_of_business=state["line_of_business"], top_k=state.get("top_k", 5))
        return {"draft_decision": decision}

    def _coverage(self, state: AgentState) -> AgentState:
        return {"draft_decision": build_coverage_response(state["question"])}

    def _provider_cost(self, state: AgentState) -> AgentState:
        return {"draft_decision": build_provider_cost_response(state["question"], pricing_path=self.pricing_path, market=state["market"])}

    def _review(self, state: AgentState) -> AgentState:
        return {"draft_decision": review_decision(state["draft_decision"])}

    def _finalize(self, state: AgentState) -> AgentState:
        decision = state["draft_decision"]
        record_query(state["route"], decision.status)
        return state

    def invoke(self, question: str, *, market: str, line_of_business: str, top_k: int = 5) -> AssistantDecision:
        result = self._compiled.invoke({"question": question, "market": market, "line_of_business": line_of_business, "top_k": top_k})
        return result["draft_decision"]


def build_graph(policy_tool: PolicySearchTool, *, pricing_path: str | Path | None = None) -> HealthPAGraph:
    return HealthPAGraph(policy_tool=policy_tool, pricing_path=pricing_path)
