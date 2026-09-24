from __future__ import annotations

import json
from pathlib import Path

from src.rag.chunker import create_policy_chunks
from src.rag.models import CoveragePolicy


INPUT_DIR = Path("data/processed/ncd")
OUTPUT_DIR = Path("data/processed/chunks")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    files = sorted(INPUT_DIR.glob("*.json"))

    print(f"Found {len(files)} normalized policies.")

    all_chunks = []

    for file in files:
        payload = json.loads(file.read_text(encoding="utf-8"))

        policy = CoveragePolicy(**payload)

        chunks = create_policy_chunks(policy)

        for chunk in chunks:
            all_chunks.append(
                {
                    "chunk_id": chunk.chunk_id,
                    "text": chunk.text,
                    "metadata": chunk.metadata,
                }
            )

        print(
            f"{policy.display_id}: "
            f"{policy.title} -> {len(chunks)} chunks"
        )

    output_file = OUTPUT_DIR / "ncd_chunks.json"

    output_file.write_text(
        json.dumps(
            all_chunks,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print()
    print(f"Created {len(all_chunks)} chunks.")
    print(f"Saved: {output_file}")


if __name__ == "__main__":
    main()