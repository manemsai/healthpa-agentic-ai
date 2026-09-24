"""Domain models for evidence-backed assistant responses."""

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field

DecisionStatus = Literal[
    "evidence_found",
    "evidence_not_found",
    "conflicting_evidence",
    "plan_verification_required",
    "human_review_required",
]

PriorAuthStatus = Literal[
    "potentially_required",
    "no_public_evidence_found",
    "unknown",
    "plan_verification_required",
]


class Evidence(BaseModel):
    """A source excerpt used to support an assistant claim."""

    source_type: str
    title: str
    source_id: str
    retrieved_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    excerpt: str
    source_url: str | None = None
    effective_date: str | None = None
    section_path: str | None = None


class AssistantDecision(BaseModel):
    """Structured response contract for grounded healthcare answers."""

    status: DecisionStatus
    summary: str
    prior_auth_status: PriorAuthStatus = "unknown"
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[Evidence] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    recommended_next_steps: list[str] = Field(default_factory=list)
