"""FAISS vector store helpers."""

from __future__ import annotations

import json
from pathlib import Path

import faiss
import numpy as np

from elevance_ai.domain.policy import PolicyChunk


class FaissPolicyIndex:
    """Small wrapper around a FAISS flat index plus JSON metadata."""

    def __init__(self, dimensions: int) -> None:
        self.dimensions = dimensions
        self.index = faiss.IndexFlatIP(dimensions)
        self.metadata: list[dict[str, object]] = []

    def add(self, chunks: list[PolicyChunk], embeddings: list[list[float]]) -> None:
        """Add chunk vectors and metadata to the index."""

        if len(chunks) != len(embeddings):
            raise ValueError("chunks and embeddings must have the same length")
        if not chunks:
            return

        matrix = np.asarray(embeddings, dtype="float32")
        if matrix.shape[1] != self.dimensions:
            raise ValueError("embedding dimension mismatch")

        self.index.add(matrix)
        self.metadata.extend(chunk.model_dump(mode="json") for chunk in chunks)

    def save(self, index_path: str | Path, metadata_path: str | Path) -> None:
        """Persist index vectors and metadata to disk."""

        index_file = Path(index_path)
        metadata_file = Path(metadata_path)
        index_file.parent.mkdir(parents=True, exist_ok=True)
        metadata_file.parent.mkdir(parents=True, exist_ok=True)

        faiss.write_index(self.index, str(index_file))
        metadata_file.write_text(json.dumps(self.metadata, ensure_ascii=True, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, index_path: str | Path, metadata_path: str | Path) -> "FaissPolicyIndex":
        """Load index vectors and metadata from disk."""

        index = faiss.read_index(str(index_path))
        metadata = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
        store = cls(index.d)
        store.index = index
        store.metadata = metadata
        return store

    def search(
        self,
        query_embedding: list[float],
        *,
        top_k: int = 5,
        market: str | None = None,
        line_of_business: str | None = None,
    ) -> list[dict[str, object]]:
        """Search vectors, then apply lightweight metadata filters."""

        if self.index.ntotal == 0:
            return []

        query = np.asarray([query_embedding], dtype="float32")
        scores, indices = self.index.search(query, min(max(top_k * 5, top_k), self.index.ntotal))

        results: list[dict[str, object]] = []
        for score, raw_index in zip(scores[0], indices[0], strict=False):
            if raw_index < 0:
                continue
            item = dict(self.metadata[raw_index])
            if market and item.get("market") != market:
                continue
            if line_of_business and item.get("line_of_business") != line_of_business:
                continue
            item["score"] = float(score)
            results.append(item)
            if len(results) >= top_k:
                break
        return results
