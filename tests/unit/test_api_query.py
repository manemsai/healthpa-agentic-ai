from datetime import date

from elevance_ai.domain.policy import PolicyChunk
from elevance_ai.rag.embeddings import LocalHashEmbeddingModel
from elevance_ai.rag.faiss_store import FaissPolicyIndex
from elevance_ai.rag.retriever import PolicyRetriever
from elevance_ai.tools.policy_tools import PolicySearchTool
from apps.api.main import PolicyQueryRequest, PolicyQueryResponse


def test_policy_query_response_contract() -> None:
    request = PolicyQueryRequest(question="Do I need prior authorization?", market="IN", line_of_business="COMMERCIAL")

    assert request.question == "Do I need prior authorization?"
    assert request.top_k == 5


def test_policy_query_response_with_evidence() -> None:
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
    tool = PolicySearchTool(PolicyRetriever(index=store, embedding_model=model))

    evidence = tool.search("prior authorization outpatient knee arthroscopy", market="IN", line_of_business="COMMERCIAL")
    response = PolicyQueryResponse.model_validate(
        {
            "decision": {
                "status": "evidence_found",
                "summary": "Relevant policy evidence was found.",
                "prior_auth_status": "plan_verification_required",
                "confidence": 0.72,
                "evidence": [item.model_dump(mode="json") for item in evidence],
                "warnings": [],
                "recommended_next_steps": [],
            },
            "evidence": [item.model_dump(mode="json") for item in evidence],
        }
    )

    assert response.decision.status == "evidence_found"
    assert response.evidence[0].source_id == "SURG-001"
