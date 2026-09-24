from __future__ import annotations

from sentence_transformers import SentenceTransformer


class LocalEmbeddingModel:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=True,
        ).tolist()

    def embed_query(self, query: str) -> list[float]:
        return self.model.encode(
            query,
            normalize_embeddings=True,
        ).tolist()