"""Tool wrappers for policy-related operations."""

from __future__ import annotations

from pathlib import Path

from elevance_ai.config import AppSettings, get_settings
from elevance_ai.domain.evidence import Evidence
from elevance_ai.domain.policy import PolicyChunk
from elevance_ai.rag.retriever import PolicyRetriever


class PolicySearchTool:
    """Policy evidence lookup over the local retrieval index."""

    def __init__(self, retriever: PolicyRetriever) -> None:
        self.retriever = retriever

    @classmethod
    def from_settings(cls, settings: AppSettings | None = None) -> "PolicySearchTool":
        """Construct the tool from application settings."""

        app_settings = settings or get_settings()
        retriever = PolicyRetriever.from_disk(
            index_path=Path(app_settings.policy_index_path),
            metadata_path=Path(app_settings.policy_metadata_path),
        )
        return cls(retriever)

    def search(
        self,
        query: str,
        *,
        market: str,
        line_of_business: str,
        top_k: int = 5,
    ) -> list[Evidence]:
        """Search policy evidence and return normalized evidence objects."""

        chunks = self.retriever.retrieve(
            query,
            market=market,
            line_of_business=line_of_business,
            top_k=top_k,
        )
        return [self._chunk_to_evidence(chunk) for chunk in chunks]

    def _chunk_to_evidence(self, chunk: PolicyChunk) -> Evidence:
        """Convert a retrieved chunk into an evidence record."""

        return Evidence(
            source_type=chunk.source_type,
            title=chunk.title,
            source_id=chunk.policy_id,
            excerpt=chunk.text,
            source_url=chunk.source_url,
            effective_date=chunk.effective_date.isoformat() if chunk.effective_date else None,
            section_path=chunk.section_path,
        )
