from __future__ import annotations

from pathlib import Path

from src.llm.bedrock_client import BedrockLLM
from src.rag.faiss_store import FAISSVectorStore
from src.rag.reranker import rerank_results
from src.rag.confidence import calculate_retrieval_confidence
from src.rag.grounding import calculate_grounding_score


INDEX_FILE = Path(
    "data/vectorstore/faiss/ncd.index"
)

METADATA_FILE = Path(
    "data/vectorstore/faiss/ncd_metadata.pkl"
)


class CMSRAGPipeline:

    def __init__(self):

        self.store = FAISSVectorStore()

        self.store.load(
            INDEX_FILE,
            METADATA_FILE,
        )

        self.llm = BedrockLLM()

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict]:

        results = self.store.search(
            query=query,
            top_k=top_k,
        )

        results = rerank_results(
            query,
            results,
        )

        return results

    def build_context(
        self,
        results: list[dict],
        top_n: int = 3,
    ) -> str:

        sections = []

        for index, result in enumerate(
            results[:top_n],
            start=1,
        ):

            metadata = result["metadata"]

            section = f"""
SOURCE {index}

NCD: {metadata.get("display_id")}
Title: {metadata.get("title")}
Section: {metadata.get("section")}
Effective Date: {metadata.get("effective_date")}
Source URL: {metadata.get("source_url")}

Policy Text:
{result["text"]}
"""

            sections.append(section)

        return "\n\n".join(sections)

    def ask(
        self,
        query: str,
    ) -> dict:

        results = self.retrieve(
            query=query,
            top_k=5,
        )

        context = self.build_context(
            results,
            top_n=3,
        )

        prompt = f"""
You are a healthcare coverage information assistant.

Answer the user's question using ONLY the CMS policy evidence supplied below.

Important rules:

1. Do not use outside medical or insurance knowledge.
2. Do not invent coverage requirements.
3. If the CMS evidence is insufficient, explicitly say that the available evidence is insufficient.
4. Clearly distinguish covered conditions from non-covered conditions.
5. Mention important limits or requirements when supported by the evidence.
6. Cite the relevant NCD number and policy title.
7. Do not make a final clinical diagnosis.
8. Do not claim that a specific patient's authorization is approved or denied.

USER QUESTION:

{query}

CMS POLICY EVIDENCE:

{context}

Provide a concise and clear answer.
"""

        answer = self.llm.generate(
            prompt
        )

        selected_sources = results[:3]

        retrieval_confidence = (
            calculate_retrieval_confidence(
                results
            )
        )

        grounding_score = (
            calculate_grounding_score(
                answer,
                selected_sources,
            )
        )

        requires_human_review = (
            retrieval_confidence < 0.60
            or grounding_score < 0.50
        )

        return {
            "query": query,
            "answer": answer,
            "retrieval_confidence": retrieval_confidence,
            "grounding_score": round(
                grounding_score,
                4,
            ),
            "requires_human_review": (
                requires_human_review
            ),
            "sources": selected_sources,
        }