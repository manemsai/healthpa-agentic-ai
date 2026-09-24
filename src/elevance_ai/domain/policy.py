"""Domain models for policy data."""

from datetime import date

from pydantic import BaseModel, Field


class PolicyDocument(BaseModel):
    """Normalized representation of a policy or UM guidance document."""

    policy_id: str
    title: str
    payer: str = "Anthem"
    market: str
    line_of_business: str
    source_url: str
    source_type: str = "medical_policy"
    source_name: str = "Anthem Public Policy"
    effective_date: date | None = None
    last_reviewed_date: date | None = None
    body_text: str = Field(repr=False)
    summary: str | None = None
    section_titles: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class PolicyChunk(BaseModel):
    """Chunked policy text stored for retrieval."""

    chunk_id: str
    policy_id: str
    title: str
    text: str
    payer: str = "Anthem"
    section_path: str | None = None
    source_url: str | None = None
    market: str
    line_of_business: str
    source_type: str = "medical_policy"
    effective_date: date | None = None
    summary: str | None = None
    tags: list[str] = Field(default_factory=list)
