"""Chunking utilities for retrieval-augmented generation."""

from __future__ import annotations

import re

from elevance_ai.domain.policy import PolicyChunk, PolicyDocument


def chunk_policy_document(
    document: PolicyDocument,
    *,
    chunk_size: int = 800,
    chunk_overlap: int = 120,
) -> list[PolicyChunk]:
    """Split a normalized policy document into retrieval chunks."""

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")
    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be non-negative and smaller than chunk_size")

    sections = _split_into_sections(document.body_text)
    chunks: list[PolicyChunk] = []
    chunk_counter = 0

    for section_path, section_text in sections:
        text = section_text.strip()
        if not text:
            continue

        windows = _sliding_windows(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        for window in windows:
            chunks.append(
                PolicyChunk(
                    chunk_id=f"{document.policy_id}-{chunk_counter:04d}",
                    policy_id=document.policy_id,
                    title=document.title,
                    text=window,
                    payer=document.payer,
                    section_path=section_path,
                    source_url=document.source_url,
                    market=document.market,
                    line_of_business=document.line_of_business,
                    source_type=document.source_type,
                    effective_date=document.effective_date,
                    summary=document.summary,
                    tags=list(document.tags),
                )
            )
            chunk_counter += 1

    return chunks


def _split_into_sections(body_text: str) -> list[tuple[str | None, str]]:
    lines = [line.strip() for line in body_text.splitlines()]
    sections: list[tuple[str | None, str]] = []
    current_heading: str | None = None
    current_lines: list[str] = []

    for line in lines:
        if not line:
            continue
        if _looks_like_heading(line):
            if current_lines:
                sections.append((current_heading, " ".join(current_lines)))
                current_lines = []
            current_heading = line
            continue
        current_lines.append(line)

    if current_lines:
        sections.append((current_heading, " ".join(current_lines)))

    if not sections:
        return [(None, body_text)]
    return sections


def _looks_like_heading(line: str) -> bool:
    if len(line) > 100:
        return False
    if line.endswith(":"):
        return True
    title_case_ratio = sum(1 for word in line.split() if word[:1].isupper()) / max(len(line.split()), 1)
    return title_case_ratio > 0.7 and len(line.split()) <= 8


def _sliding_windows(text: str, *, chunk_size: int, chunk_overlap: int) -> list[str]:
    normalized = re.sub(r"\s+", " ", text).strip()
    if len(normalized) <= chunk_size:
        return [normalized]

    windows: list[str] = []
    start = 0
    step = chunk_size - chunk_overlap

    while start < len(normalized):
        end = min(start + chunk_size, len(normalized))
        if end < len(normalized):
            split_at = normalized.rfind(" ", start, end)
            if split_at > start + 50:
                end = split_at
        window = normalized[start:end].strip()
        if window:
            windows.append(window)
        if end >= len(normalized):
            break
        start = max(end - chunk_overlap, start + step)

    return windows
