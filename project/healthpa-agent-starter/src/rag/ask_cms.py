from src.rag.rag_pipeline import CMSRAGPipeline


def main():

    rag = CMSRAGPipeline()

    print("=" * 80)
    print("HealthPA CMS RAG Assistant")
    print("=" * 80)

    while True:

        query = input(
            "\nAsk a CMS coverage question "
            "(or type exit): "
        ).strip()

        if query.lower() in {
            "exit",
            "quit",
            "q",
        }:
            break

        result = rag.ask(query)

        print()
        print("=" * 80)
        print("ANSWER")
        print("=" * 80)

        print(result["answer"])
        print()
        print("=" * 80)
        print("QUALITY CHECKS")
        print("=" * 80)

        print(
            f"Retrieval Confidence: "
            f"{result['retrieval_confidence']:.4f}"
        )

        print(
            f"Grounding Score: "
            f"{result['grounding_score']:.4f}"
        )

        print(
            f"Human Review Required: "
            f"{result['requires_human_review']}"
        )

        print()
        print("=" * 80)
        print("RETRIEVED SOURCES")
        print("=" * 80)

        for source in result["sources"]:

            metadata = source["metadata"]

            print(
                f"NCD {metadata.get('display_id')} | "
                f"{metadata.get('title')} | "
                f"{metadata.get('section')}"
            )


if __name__ == "__main__":
    main()