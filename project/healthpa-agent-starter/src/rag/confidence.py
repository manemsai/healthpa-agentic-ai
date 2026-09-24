from __future__ import annotations


def calculate_retrieval_confidence(
    results: list[dict],
) -> float:

    if not results:
        return 0.0

    top_score = results[0].get(
        "rerank_score",
        results[0].get("score", 0.0),
    )

    second_score = 0.0

    if len(results) > 1:
        second_score = results[1].get(
            "rerank_score",
            results[1].get("score", 0.0),
        )

    score_component = min(
        max(top_score, 0.0),
        1.0,
    )

    margin = max(
        top_score - second_score,
        0.0,
    )

    margin_component = min(
        margin * 2,
        1.0,
    )

    confidence = (
        0.8 * score_component
        +
        0.2 * margin_component
    )

    return round(confidence, 4)