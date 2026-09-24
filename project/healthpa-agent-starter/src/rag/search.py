from __future__ import annotations

from pathlib import Path

from src.rag.faiss_store import FAISSVectorStore

from src.rag.reranker import rerank_results


INDEX_FILE = Path(
    "data/vectorstore/faiss/ncd.index"
)

METADATA_FILE = Path(
    "data/vectorstore/faiss/ncd_metadata.pkl"
)


def main():

    store = FAISSVectorStore()

    store.load(
        INDEX_FILE,
        METADATA_FILE,
    )

    print()
    print("=" * 80)
    print("CMS COVERAGE SEMANTIC SEARCH")
    print("=" * 80)

    while True:

        query = input(
            "\nEnter your healthcare question "
            "(or type exit): "
        ).strip()

        if query.lower() in {
            "exit",
            "quit",
            "q",
        }:
            break

        results = store.search(
            query=query,
            top_k=5,
        )
        results = rerank_results(
            query,
            results,
        )
        

        print()
        print("=" * 80)
        print("TOP RESULTS")
        print("=" * 80)

        for i, result in enumerate(
            results,
            start=1,
        ):

            metadata = result[
                "metadata"
            ]

            print()
            print(
                f"RESULT {i}"
            )

            print(
                f"Vector Score: "
                f"{result['score']:.4f}"
            )

            print(
                f"Rerank Score: "
                f"{result['rerank_score']:.4f}"
            )
            

            print(
                f"Policy: "
                f"{metadata.get('display_id')}"
            )

            print(
                f"Title: "
                f"{metadata.get('title')}"
            )

            print(
                f"Section: "
                f"{metadata.get('section')}"
            )

            print(
                f"Chunk ID: "
                f"{result['chunk_id']}"
            )

            print()
            print(
                result["text"][:1200]
            )

            print()
            print("-" * 80)


if __name__ == "__main__":
    main()