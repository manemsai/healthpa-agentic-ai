from datetime import date

from elevance_ai.agents.graph import build_graph
from elevance_ai.agents.reviewer import review_decision
from elevance_ai.agents.router import route_question
from elevance_ai.domain.evidence import AssistantDecision
from elevance_ai.domain.policy import PolicyChunk
from elevance_ai.rag.embeddings import LocalHashEmbeddingModel
from elevance_ai.rag.faiss_store import FaissPolicyIndex
from elevance_ai.rag.retriever import PolicyRetriever
from elevance_ai.tools.policy_tools import PolicySearchTool


def _policy_tool() -> PolicySearchTool:
    chunk = PolicyChunk(
        chunk_id="SURG-001-0000",
        policy_id="SURG-001",
        title="Knee Arthroscopy Policy",
        text="Prior authorization may be required for outpatient knee arthroscopy.",
        payer="Anthem",
        market="IN",
        line_of_business="COMMERCIAL",
        source_url="https://example.org/policies/surg-001",
        source_type="medical_policy",
        effective_date=date(2026, 1, 15),
    )
    model = LocalHashEmbeddingModel(dimensions=64)
    store = FaissPolicyIndex(dimensions=64)
    store.add([chunk], model.embed_documents([chunk.text]))
    return PolicySearchTool(PolicyRetriever(index=store, embedding_model=model))


def test_route_question_selects_expected_agent() -> None:
    assert route_question("Is prior authorization required?") == "policy"
    assert route_question("What is the negotiated rate for CPT 99213?") == "provider_cost"
    assert route_question("Does my plan cover this claim?") == "coverage"


def test_graph_returns_policy_evidence() -> None:
    decision = build_graph(_policy_tool()).invoke(
        "prior authorization outpatient knee arthroscopy",
        market="IN",
        line_of_business="COMMERCIAL",
    )

    assert decision.status == "evidence_found"
    assert decision.evidence[0].source_id == "SURG-001"
    assert decision.prior_auth_status == "plan_verification_required"


def test_reviewer_flags_final_decision_language() -> None:
    decision = AssistantDecision(
        status="evidence_found",
        summary="This request is approved.",
        prior_auth_status="potentially_required",
        confidence=0.9,
    )

    reviewed = review_decision(decision)

    assert reviewed.status == "human_review_required"
    assert reviewed.confidence == 0.4
    assert reviewed.warnings
