"""Retriever implementations for RAG workflows."""

from __future__ import annotations

from pathlib import Path

from elevance_ai.domain.policy import PolicyChunk
from elevance_ai.rag.embeddings import LocalHashEmbeddingModel
from elevance_ai.rag.faiss_store import FaissPolicyIndex
from elevance_ai.rag.reranker import overlap_rerank


class PolicyRetriever:
    """Local policy retriever backed by FAISS and deterministic embeddings."""

    def __init__(
        self,
        *,
        index: FaissPolicyIndex,
        embedding_model: LocalHashEmbeddingModel,
    ) -> None:
        self.index = index
        self.embedding_model = embedding_model

    @classmethod
    def from_disk(
        cls,
        *,
        index_path: str | Path,
        metadata_path: str | Path,
        embedding_dimensions: int = 256,
    ) -> "PolicyRetriever":
        """Load a retriever from persisted local artifacts."""

        return cls(
            index=FaissPolicyIndex.load(index_path, metadata_path),
            embedding_model=LocalHashEmbeddingModel(dimensions=embedding_dimensions),
        )

    def retrieve(
        self,
        query: str,
        *,
        market: str,
        line_of_business: str,
        top_k: int = 5,
    ) -> list[PolicyChunk]:
        """Retrieve and rerank relevant policy chunks for a query."""

        query_embedding = self.embedding_model.embed_query(query)
        raw_results = self.index.search(
            query_embedding,
            top_k=top_k,
            market=market,
            line_of_business=line_of_business,
        )
        reranked = overlap_rerank(query, raw_results)
        return [PolicyChunk.model_validate(item) for item in reranked[:top_k]]
