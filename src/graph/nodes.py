from __future__ import annotations

from src.llm.bedrock_client import BedrockLLM
from src.rag.confidence import calculate_retrieval_confidence
from src.rag.grounding import calculate_grounding_score
from src.rag.rag_pipeline import CMSRAGPipeline
from src.rag.reranker import rerank_results

from src.graph.state import HealthPAState


rag_pipeline = CMSRAGPipeline()
llm = BedrockLLM()


def router_node(
    state: HealthPAState,
) -> HealthPAState:

    query = state["query"].lower()

    coverage_keywords = [
        "covered",
        "coverage",
        "medicare",
        "ncd",
        "policy",
        "treatment",
        "procedure",
        "authorization",
    ]

    if any(
        word in query
        for word in coverage_keywords
    ):
        intent = "coverage"

    else:
        intent = "unknown"

    print(
        f"[Router] Intent detected: {intent}"
    )

    return {
        "intent": intent
    }


def retrieval_node(
    state: HealthPAState,
) -> HealthPAState:

    query = state["query"]

    print(
        "[Retrieval] Searching CMS policies..."
    )

    results = rag_pipeline.store.search(
        query=query,
        top_k=5,
    )

    results = rerank_results(
        query,
        results,
    )

    selected_sources = results[:3]

    retrieval_confidence = (
        calculate_retrieval_confidence(
            results
        )
    )

    print(
        f"[Retrieval] Confidence: "
        f"{retrieval_confidence}"
    )

    return {
        "retrieved_results": results,
        "selected_sources": selected_sources,
        "retrieval_confidence": (
            retrieval_confidence
        ),
    }

def evidence_check_node(
    state: HealthPAState,
) -> HealthPAState:

    query = state["query"].lower()
    sources = state.get("selected_sources", [])

    score = state.get("retrieval_confidence", 0.0)

    # Our current knowledge base contains Medicare NCDs,
    # not Elevance-specific authorization policies.
    payer_specific = any(
        term in query
        for term in ["elevance", "anthem"]
    )

    authorization_specific = any(
        term in query
        for term in [
            "prior authorization",
            "preauthorization",
            "pre-authorization",
        ]
    )

    if payer_specific or authorization_specific:
        return {
            "evidence_sufficient": False,
            "review_reason": (
                "The current dataset does not establish "
                "payer-specific authorization requirements."
            ),
        }

    # Conservative experimental threshold.
    # This score is not a calibrated probability.
    if not sources or score < 0.55:
        return {
            "evidence_sufficient": False,
            "review_reason": (
                "Insufficient relevant CMS evidence."
            ),
        }

    return {
        "evidence_sufficient": True,
        "review_reason": "",
    }

def human_review_node(
    state: HealthPAState,
) -> HealthPAState:

    reason = state.get(
        "review_reason"
    ) or "Automated quality checks require verification."

    print(f"[Human Review] {reason}")

    return {
        "answer": (
            "I cannot determine coverage from the "
            "available evidence. Additional policy "
            "verification is required."
        ),
        "requires_human_review": True,
        "review_reason": reason,
        "final_status": "PENDING_HUMAN_REVIEW",
    }


def generation_node(
    state: HealthPAState,
) -> HealthPAState:

    query = state["query"]

    sources = state.get(
        "selected_sources",
        [],
    )

    print(
        "[Generation] Creating grounded answer..."
    )

    context = rag_pipeline.build_context(
        sources,
        top_n=3,
    )

    prompt = f"""
You are a healthcare coverage information assistant.

Answer the user question using ONLY the CMS policy evidence below.

Rules:

1. Do not use outside knowledge.
2. Do not invent coverage rules.
3. If evidence is insufficient, clearly state that.
4. Distinguish covered and non-covered conditions.
5. Include limits and requirements when supported.
6. Cite the applicable NCD number and title.
7. Do not diagnose the patient.
8. Do not claim that an authorization is approved or denied.

USER QUESTION:

{query}

CMS POLICY EVIDENCE:

{context}

Provide a concise, clear answer.
"""

    answer = llm.generate(
        prompt
    )

    return {
        "answer": answer
    }


def grounding_node(
    state: HealthPAState,
) -> HealthPAState:

    answer = state.get(
        "answer",
        "",
    )

    sources = state.get(
        "selected_sources",
        [],
    )

    grounding_score = (
        calculate_grounding_score(
            answer,
            sources,
        )
    )

    print(
        f"[Grounding] Score: "
        f"{grounding_score:.4f}"
    )

    return {
        "grounding_score": round(
            grounding_score,
            4,
        )
    }


def review_decision_node(
    state: HealthPAState,
) -> HealthPAState:

    retrieval_confidence = (
        state.get(
            "retrieval_confidence",
            0.0,
        )
    )

    grounding_score = (
        state.get(
            "grounding_score",
            0.0,
        )
    )

    requires_review = (
        retrieval_confidence < 0.60
        or grounding_score < 0.50
    )

    print(
        f"[Review Decision] "
        f"Human review: {requires_review}"
    )

    return {
        "requires_human_review": (
            requires_review
        )
    }


def human_review_node(
    state: HealthPAState,
) -> HealthPAState:

    reason = state.get(
        "review_reason"
    ) or "Automated quality checks require additional verification."

    print(f"[Human Review] {reason}")

    return {
        "answer": (
            "The available evidence is insufficient to provide "
            "a reliable coverage determination. Additional policy "
            "verification is required."
        ),
        "requires_human_review": True,
        "review_reason": reason,
        "final_status": "PENDING_HUMAN_REVIEW",
    }

def final_response_node(
    state: HealthPAState,
) -> HealthPAState:

    print(
        "[Final Response] "
        "Answer accepted."
    )

    return {
        "final_status": "COMPLETED"
    }