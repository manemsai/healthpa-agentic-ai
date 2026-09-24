from __future__ import annotations

import json
from pathlib import Path

from src.rag.faiss_store import FAISSVectorStore


CHUNKS_FILE = Path(
    "data/processed/chunks/ncd_chunks.json"
)

INDEX_FILE = Path(
    "data/vectorstore/faiss/ncd.index"
)

METADATA_FILE = Path(
    "data/vectorstore/faiss/ncd_metadata.pkl"
)


def main():

    chunks = json.loads(
        CHUNKS_FILE.read_text(
            encoding="utf-8"
        )
    )

    print(
        f"Loaded {len(chunks)} chunks."
    )

    store = FAISSVectorStore()

    store.build(chunks)

    store.save(
        INDEX_FILE,
        METADATA_FILE,
    )

    print()
    print("FAISS index saved.")
    print(f"Index: {INDEX_FILE}")
    print(f"Metadata: {METADATA_FILE}")


if __name__ == "__main__":
    main()