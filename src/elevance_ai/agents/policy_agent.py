"""Evidence-first policy assistant service."""
from __future__ import annotations

from dataclasses import dataclass

from elevance_ai.domain.evidence import AssistantDecision, Evidence
from elevance_ai.tools.policy_tools import PolicySearchTool


@dataclass(slots=True)
class PolicyAgent:
    """Retrieve policy evidence and return a conservative decision envelope."""

    tool: PolicySearchTool

    def answer(self, question: str, *, market: str, line_of_business: str, top_k: int = 5) -> AssistantDecision:
        evidence = self.tool.search(question, market=market, line_of_business=line_of_business, top_k=top_k)
        return build_decision(evidence)


def build_decision(evidence: list[Evidence]) -> AssistantDecision:
    if evidence:
        return AssistantDecision(status="evidence_found", summary="Relevant public policy evidence was found; member-specific coverage still requires plan verification.", prior_auth_status="plan_verification_required", confidence=0.72, evidence=evidence, warnings=["Public policy evidence is not a final benefit or authorization determination."], recommended_next_steps=["Review the cited policy sections.", "Verify member-specific benefits and authorization requirements."])
    return AssistantDecision(status="evidence_not_found", summary="No relevant evidence was retrieved from the configured local policy index.", prior_auth_status="no_public_evidence_found", confidence=0.2, evidence=[], warnings=["The local index may not contain the relevant policy."], recommended_next_steps=["Ingest additional policy documents and rebuild the index.", "Escalate to authorized plan verification."])
