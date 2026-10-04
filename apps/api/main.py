"""FastAPI entrypoint for the Elevance AI API."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from elevance_ai import get_settings
from elevance_ai.agents.graph import build_graph
from elevance_ai.domain.evidence import AssistantDecision, Evidence
from elevance_ai.observability.logging import configure_logging
from elevance_ai.observability.metrics import snapshot
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


configure_logging()
settings = get_settings()
policy_tool: PolicySearchTool | None = None


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Load local retrieval resources for the application lifecycle."""

    global policy_tool
    try:
        policy_tool = PolicySearchTool.from_settings(settings)
    except (OSError, RuntimeError, ValueError, ImportError):
        policy_tool = None
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Evidence-first healthcare policy retrieval API",
    lifespan=lifespan,
)


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


@app.get("/metrics")
def metrics() -> dict[str, int]:
    """Return non-sensitive process-local aggregate counters."""
    return snapshot()


@app.post("/query", response_model=PolicyQueryResponse)
def query_policy(request: PolicyQueryRequest) -> PolicyQueryResponse:
    """Return grounded policy evidence for a user question."""

    global policy_tool
    tool = policy_tool
    if tool is None:
        try:
            tool = PolicySearchTool.from_settings(settings)
            policy_tool = tool
        except (OSError, RuntimeError, ValueError, ImportError):
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
    decision = build_graph(tool, pricing_path=settings.pricing_data_path).invoke(
        request.question,
        market=market,
        line_of_business=line_of_business,
        top_k=request.top_k,
    )
    evidence = decision.evidence

    return PolicyQueryResponse(decision=decision, evidence=evidence)
