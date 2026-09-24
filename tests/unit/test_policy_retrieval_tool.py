from datetime import date

from elevance_ai.domain.policy import PolicyChunk
from elevance_ai.rag.embeddings import LocalHashEmbeddingModel
from elevance_ai.rag.faiss_store import FaissPolicyIndex
from elevance_ai.rag.retriever import PolicyRetriever
from elevance_ai.tools.policy_tools import PolicySearchTool


def test_policy_retriever_returns_filtered_chunks() -> None:
    chunks = [
        PolicyChunk(
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
        ),
        PolicyChunk(
            chunk_id="CARD-001-0000",
            policy_id="CARD-001",
            title="Cardiac Imaging Policy",
            text="Cardiac imaging criteria for outpatient diagnostic services.",
            payer="Anthem",
            market="OH",
            line_of_business="COMMERCIAL",
            source_url="https://example.org/policies/card-001",
            source_type="medical_policy",
            effective_date=date(2026, 2, 1),
        ),
    ]
    model = LocalHashEmbeddingModel(dimensions=64)
    store = FaissPolicyIndex(dimensions=64)
    store.add(chunks, model.embed_documents([chunk.text for chunk in chunks]))

    retriever = PolicyRetriever(index=store, embedding_model=model)
    results = retriever.retrieve(
        "knee arthroscopy prior authorization",
        market="IN",
        line_of_business="COMMERCIAL",
        top_k=3,
    )

    assert results
    assert results[0].policy_id == "SURG-001"
    assert all(result.market == "IN" for result in results)


def test_policy_search_tool_returns_evidence_objects() -> None:
    chunk = PolicyChunk(
        chunk_id="SURG-001-0000",
        policy_id="SURG-001",
        title="Knee Arthroscopy Policy",
        text="Medical necessity must be documented for outpatient knee arthroscopy.",
        payer="Anthem",
        market="IN",
        line_of_business="COMMERCIAL",
        source_url="https://example.org/policies/surg-001",
        source_type="medical_policy",
        effective_date=date(2026, 1, 15),
        section_path="Criteria",
    )
    model = LocalHashEmbeddingModel(dimensions=64)
    store = FaissPolicyIndex(dimensions=64)
    store.add([chunk], model.embed_documents([chunk.text]))

    tool = PolicySearchTool(PolicyRetriever(index=store, embedding_model=model))
    evidence = tool.search(
        "outpatient knee arthroscopy documentation",
        market="IN",
        line_of_business="COMMERCIAL",
        top_k=1,
    )

    assert len(evidence) == 1
    assert evidence[0].source_id == "SURG-001"
    assert evidence[0].effective_date == "2026-01-15"
    assert evidence[0].section_path == "Criteria"
