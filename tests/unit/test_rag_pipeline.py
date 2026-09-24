import json
from pathlib import Path

from elevance_ai.domain.policy import PolicyDocument
from elevance_ai.rag.chunking import chunk_policy_document
from elevance_ai.rag.embeddings import LocalHashEmbeddingModel
from elevance_ai.rag.faiss_store import FaissPolicyIndex
from scripts.build_index import load_policy_documents


def test_chunk_policy_document_preserves_metadata() -> None:
    document = PolicyDocument(
        policy_id="SURG-001",
        title="Medical Policy SURG-001 Knee Arthroscopy",
        market="IN",
        line_of_business="COMMERCIAL",
        source_url="https://example.org/policies/surg-001",
        body_text="Overview:\nPrior authorization may be required.\nCriteria:\nMedical necessity must be documented.",
        tags=["prior_authorization"],
    )

    chunks = chunk_policy_document(document, chunk_size=50, chunk_overlap=10)

    assert chunks
    assert chunks[0].policy_id == "SURG-001"
    assert chunks[0].title == document.title
    assert chunks[0].market == "IN"
    assert chunks[0].tags == ["prior_authorization"]


def test_faiss_index_search_returns_filtered_results() -> None:
    model = LocalHashEmbeddingModel(dimensions=64)
    documents = [
        PolicyDocument(
            policy_id="SURG-001",
            title="Knee Arthroscopy Policy",
            market="IN",
            line_of_business="COMMERCIAL",
            source_url="https://example.org/1",
            body_text="Prior authorization may be required for arthroscopy procedures.",
        ),
        PolicyDocument(
            policy_id="CARD-001",
            title="Cardiac Imaging Policy",
            market="OH",
            line_of_business="COMMERCIAL",
            source_url="https://example.org/2",
            body_text="Cardiac imaging criteria for outpatient diagnostic services.",
        ),
    ]
    chunks = [chunk for document in documents for chunk in chunk_policy_document(document)]
    embeddings = model.embed_documents([chunk.text for chunk in chunks])

    store = FaissPolicyIndex(dimensions=64)
    store.add(chunks, embeddings)
    results = store.search(
        model.embed_query("arthroscopy prior authorization"),
        top_k=3,
        market="IN",
        line_of_business="COMMERCIAL",
    )

    assert results
    assert results[0]["policy_id"] == "SURG-001"
    assert all(result["market"] == "IN" for result in results)


def test_load_policy_documents_reads_jsonl(tmp_path: Path) -> None:
    input_path = tmp_path / "policies.jsonl"
    documents = [
        {
            "policy_id": "SURG-001",
            "title": "Knee Arthroscopy Policy",
            "market": "IN",
            "line_of_business": "COMMERCIAL",
            "source_url": "https://example.org/1",
            "body_text": "Example policy text",
        }
    ]
    input_path.write_text("\n".join(json.dumps(item) for item in documents), encoding="utf-8")

    loaded = load_policy_documents(input_path)

    assert len(loaded) == 1
    assert loaded[0].policy_id == "SURG-001"
