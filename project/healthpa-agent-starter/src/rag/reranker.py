from __future__ import annotations


def rerank_results(
    query: str,
    results: list[dict],
) -> list[dict]:

    query_lower = query.lower()

    for result in results:
        score = result["score"]

        metadata = result["metadata"]

        title = metadata.get(
            "title",
            ""
        ).lower()

        section = metadata.get(
            "section",
            ""
        ).lower()

        text = result.get(
            "text",
            ""
        ).lower()

        bonus = 0.0

        # Prefer exact disease/topic wording in title
        if (
            "chronic lower back pain"
            in query_lower
            and
            "chronic lower back pain"
            in title
        ):
            bonus += 0.15

        # Prefer covered indication sections
        if "covered indications" in section:
            bonus += 0.05

        # Penalize clearly non-covered sections
        if "non-covered" in section:
            bonus -= 0.05

        result["rerank_score"] = (
            score + bonus
        )

    return sorted(
        results,
        key=lambda x: x["rerank_score"],
        reverse=True,
    )