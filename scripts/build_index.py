"""Script entrypoint for vector index construction."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from elevance_ai.config import get_settings
from elevance_ai.domain.policy import PolicyDocument
from elevance_ai.rag.chunking import chunk_policy_document
from elevance_ai.rag.embeddings import LocalHashEmbeddingModel
from elevance_ai.rag.faiss_store import FaissPolicyIndex


def build_parser() -> argparse.ArgumentParser:
    """Create a CLI parser for local FAISS policy indexing."""

    parser = argparse.ArgumentParser(description="Build a local FAISS index from normalized policy JSONL.")
    parser.add_argument("--input", default=None, help="Input JSONL path from policy ingestion.")
    parser.add_argument("--index-path", default=None, help="Output FAISS index path.")
    parser.add_argument("--metadata-path", default=None, help="Output JSON metadata path.")
    parser.add_argument("--chunk-size", type=int, default=800, help="Chunk size in characters.")
    parser.add_argument("--chunk-overlap", type=int, default=120, help="Overlap in characters between chunks.")
    parser.add_argument("--embedding-dimensions", type=int, default=256, help="Local embedding vector size.")
    return parser


def main() -> None:
    """Build a local searchable FAISS index for policy retrieval."""

    args = build_parser().parse_args()
    settings = get_settings()
    input_path = Path(args.input or settings.policy_raw_output_path)
    index_path = args.index_path or settings.policy_index_path
    metadata_path = args.metadata_path or settings.policy_metadata_path

    documents = load_policy_documents(input_path)
    chunks = [
        chunk
        for document in documents
        for chunk in chunk_policy_document(
            document,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
        )
    ]

    model = LocalHashEmbeddingModel(dimensions=args.embedding_dimensions)
    embeddings = model.embed_documents([chunk.text for chunk in chunks])
    store = FaissPolicyIndex(dimensions=args.embedding_dimensions)
    store.add(chunks, embeddings)
    store.save(index_path, metadata_path)

    print(
        f"Indexed {len(documents)} documents into {len(chunks)} chunks. "
        f"Saved vectors to {index_path} and metadata to {metadata_path}"
    )


def load_policy_documents(input_path: Path) -> list[PolicyDocument]:
    """Load normalized policy documents from JSONL."""

    documents: list[PolicyDocument] = []
    with input_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            payload = line.strip()
            if not payload:
                continue
            documents.append(PolicyDocument.model_validate(json.loads(payload)))
    return documents


if __name__ == "__main__":
    main()
