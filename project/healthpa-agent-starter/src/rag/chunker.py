from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from src.rag.models import CoveragePolicy


@dataclass
class PolicyChunk:
    chunk_id: str
    text: str
    metadata: dict[str, Any]


SECTION_PATTERN = re.compile(
    r"(?m)^(A\. General|"
    r"B\. Nationally Covered Indications|"
    r"C\. Nationally Non-Covered Indications|"
    r"D\. Other)\s*$"
)


def split_sections(text: str) -> list[tuple[str, str]]:
    if not text:
        return []

    matches = list(SECTION_PATTERN.finditer(text))

    if not matches:
        return [("Policy Content", text.strip())]

    sections = []

    for i, match in enumerate(matches):
        section_name = match.group(1)

        start = match.end()

        if i + 1 < len(matches):
            end = matches[i + 1].start()
        else:
            end = len(text)

        section_text = text[start:end].strip()

        if section_text:
            sections.append((section_name, section_text))

    return sections


def create_policy_chunks(policy: CoveragePolicy) -> list[PolicyChunk]:
    chunks: list[PolicyChunk] = []

    base_metadata = {
        "document_id": policy.document_id,
        "document_version": policy.document_version,
        "display_id": policy.display_id,
        "document_type": policy.document_type,
        "title": policy.title,
        "effective_date": policy.effective_date,
        "effective_end_date": policy.effective_end_date,
        "source": policy.source,
        "source_url": policy.source_url,
    }

    if policy.service_description:
        chunks.append(
            PolicyChunk(
                chunk_id=f"{policy.document_id}_general",
                text=policy.service_description,
                metadata={
                    **base_metadata,
                    "section": "General",
                },
            )
        )

    if policy.indications_limitations:
        sections = split_sections(policy.indications_limitations)

        for index, (section_name, section_text) in enumerate(sections):
            chunks.append(
                PolicyChunk(
                    chunk_id=f"{policy.document_id}_section_{index}",
                    text=section_text,
                    metadata={
                        **base_metadata,
                        "section": section_name,
                    },
                )
            )

    return chunks