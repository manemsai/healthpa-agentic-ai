from __future__ import annotations


def calculate_grounding_score(
    answer: str,
    sources: list[dict],
) -> float:
    """
    Lightweight lexical grounding check.

    This is not our final production evaluator.
    Later we will replace/augment this with an LLM judge
    or Bedrock Guardrails contextual grounding.
    """

    if not answer or not sources:
        return 0.0

    source_text = " ".join(
        source["text"]
        for source in sources
    ).lower()

    answer_words = {
        word.strip(".,:;!?()[]{}").lower()
        for word in answer.split()
        if len(word) > 4
    }

    if not answer_words:
        return 0.0

    supported = sum(
        1
        for word in answer_words
        if word in source_text
    )

    return supported / len(answer_words)