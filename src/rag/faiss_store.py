from __future__ import annotations

import json
import pickle
from pathlib import Path

import faiss
import numpy as np

from src.rag.embeddings import LocalEmbeddingModel


class FAISSVectorStore:
    def __init__(self):
        self.embedding_model = LocalEmbeddingModel()

        self.index = None
        self.documents = []

    def build(self, chunks: list[dict]) -> None:
        texts = [chunk["text"] for chunk in chunks]

        print(f"Creating embeddings for {len(texts)} chunks...")

        embeddings = self.embedding_model.embed_documents(texts)

        vectors = np.array(
            embeddings,
            dtype="float32"
        )

        dimension = vectors.shape[1]

        self.index = faiss.IndexFlatIP(dimension)

        self.index.add(vectors)

        self.documents = chunks

        print(f"FAISS index contains {self.index.ntotal} vectors.")

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict]:

        query_embedding = self.embedding_model.embed_query(query)

        query_vector = np.array(
            [query_embedding],
            dtype="float32"
        )

        scores, indexes = self.index.search(
            query_vector,
            top_k
        )

        results = []

        for score, index in zip(scores[0], indexes[0]):

            if index == -1:
                continue

            chunk = self.documents[index]

            results.append(
                {
                    "score": float(score),
                    "chunk_id": chunk["chunk_id"],
                    "text": chunk["text"],
                    "metadata": chunk["metadata"],
                }
            )

        return results

    def save(
        self,
        index_path: Path,
        metadata_path: Path,
    ) -> None:

        index_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        faiss.write_index(
            self.index,
            str(index_path)
        )

        with metadata_path.open("wb") as f:
            pickle.dump(
                self.documents,
                f
            )

    def load(
        self,
        index_path: Path,
        metadata_path: Path,
    ) -> None:

        self.index = faiss.read_index(
            str(index_path)
        )

        with metadata_path.open("rb") as f:
            self.documents = pickle.load(f)