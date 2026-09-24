"""Reranking utilities for retrieved results."""

from __future__ import annotations

import re


def overlap_rerank(query: str, candidates: list[dict[str, object]]) -> list[dict[str, object]]:
    """Boost candidates whose text overlaps strongly with the query terms."""

    query_terms = set(_tokenize(query))
    rescored: list[dict[str, object]] = []

    for candidate in candidates:
        text = str(candidate.get("text", ""))
        title = str(candidate.get("title", ""))
        overlap = query_terms.intersection(_tokenize(f"{title} {text}"))
        score = float(candidate.get("score", 0.0))
        adjusted = dict(candidate)
        adjusted["score"] = score + (0.05 * len(overlap))
        rescored.append(adjusted)

    rescored.sort(key=lambda item: float(item.get("score", 0.0)), reverse=True)
    return rescored


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())
