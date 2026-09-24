"""FastAPI entrypoint for the Elevance AI API."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from elevance_ai import get_settings
from elevance_ai.domain.evidence import AssistantDecision, Evidence
from elevance_ai.tools.policy_tools import PolicySearchTool


class HealthResponse(BaseModel):
    """API response model for service health."""

    status: str
    environment: str
    payer: str
    market: str
    line_of_business: str


class PolicyQueryRequest(BaseModel):
    """Request payload for policy evidence search."""

    question: str = Field(min_length=3)
    market: str | None = None
    line_of_business: str | None = None
    top_k: int = Field(default=5, ge=1, le=10)


class PolicyQueryResponse(BaseModel):
    """Response payload for policy evidence search."""

    decision: AssistantDecision
    evidence: list[Evidence]


settings = get_settings()
app = FastAPI(title=settings.app_name)
policy_tool: PolicySearchTool | None = None


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Basic health endpoint used by local and deployed environments."""

    return HealthResponse(
        status="ok",
        environment=settings.environment,
        payer=settings.payer_name,
        market=settings.payer_market,
        line_of_business=settings.line_of_business,
    )


@app.on_event("startup")
def _load_policy_tool() -> None:
    """Load the local policy tool when the API starts."""

    global policy_tool
    try:
        policy_tool = PolicySearchTool.from_settings(settings)
    except Exception:
        policy_tool = None


@app.post("/query", response_model=PolicyQueryResponse)
def query_policy(request: PolicyQueryRequest) -> PolicyQueryResponse:
    """Return grounded policy evidence for a user question."""

    global policy_tool
    tool = policy_tool
    if tool is None:
        try:
            tool = PolicySearchTool.from_settings(settings)
            policy_tool = tool
        except Exception:
            tool = None
    if tool is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "Policy index is not available. Run the index build step first "
                "or confirm the FAISS and metadata files exist."
            ),
        )

    market = request.market or settings.payer_market
    line_of_business = request.line_of_business or settings.line_of_business
    evidence = tool.search(
        request.question,
        market=market,
        line_of_business=line_of_business,
        top_k=request.top_k,
    )

    if evidence:
        decision = AssistantDecision(
            status="evidence_found",
            summary="Relevant policy evidence was found. Public policy data alone does not determine member-specific coverage or prior authorization.",
            prior_auth_status="plan_verification_required",
            confidence=0.72,
            evidence=evidence,
            warnings=[
                "Public policy evidence is not a final benefit or authorization determination.",
                "Use plan verification or authorized review before making operational decisions.",
            ],
            recommended_next_steps=[
                "Review the cited policy sections.",
                "Verify the member's specific plan benefits and authorization requirements.",
            ],
        )
    else:
        decision = AssistantDecision(
            status="evidence_not_found",
            summary="No relevant policy evidence was retrieved from the local index.",
            prior_auth_status="no_public_evidence_found",
            confidence=0.2,
            evidence=[],
            warnings=[
                "The local index may be missing the relevant policy or may not have been built yet.",
            ],
            recommended_next_steps=[
                "Ingest more policy documents.",
                "Rebuild the index after ingestion.",
            ],
        )

    return PolicyQueryResponse(decision=decision, evidence=evidence)
