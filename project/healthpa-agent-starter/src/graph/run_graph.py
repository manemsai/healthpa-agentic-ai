from __future__ import annotations

from src.graph.workflow import (
    build_graph,
)


def main():

    graph = build_graph()

    print(
        "=" * 80
    )

    print(
        "HealthPA Agentic Coverage Assistant"
    )

    print(
        "=" * 80
    )

    while True:

        query = input(
            "\nAsk a question "
            "(or type exit): "
        ).strip()

        if query.lower() in {
            "exit",
            "quit",
            "q",
        }:
            break

        initial_state = {
            "query": query
        }

        result = graph.invoke(
            initial_state
        )

        print()
        print(
            "=" * 80
        )

        print(
            "FINAL ANSWER"
        )

        print(
            "=" * 80
        )

        print(
            result.get(
                "answer"
            )
        )

        print()
        print(
            "Status:",
            result.get(
                "final_status"
            ),
        )

        print(
            "Retrieval Confidence:",
            result.get(
                "retrieval_confidence"
            ),
        )

        print(
            "Grounding Score:",
            result.get(
                "grounding_score"
            ),
        )

        print(
            "Human Review:",
            result.get(
                "requires_human_review"
            ),
        )


if __name__ == "__main__":
    main()