"""Provider cost agent backed by normalized public pricing observations."""
from __future__ import annotations

import re
from pathlib import Path

from elevance_ai.domain.evidence import AssistantDecision, Evidence
from elevance_ai.domain.pricing import PricingQuery
from elevance_ai.tools.pricing_tools import read_pricing_csv

_CODE = re.compile(r"\b(?:CPT\s*)?(\d{5})\b", re.IGNORECASE)


def build_provider_cost_response(question: str, *, pricing_path: str | Path | None = None, market: str = "IN") -> AssistantDecision:
    """Return public negotiated-rate evidence when a billing code and local data are available."""
    match = _CODE.search(question)
    path = Path(pricing_path) if pricing_path else None
    if not match or path is None or not path.is_file():
        return _unavailable_response()
    code = match.group(1)
    observations = read_pricing_csv(path, PricingQuery(billing_code=code, market=market, limit=5))
    if not observations:
        return _unavailable_response(f"No normalized public pricing observations were found for CPT {code}.")
    evidence = [Evidence(source_type="public_price_transparency", title=f"Negotiated rate observation for CPT {code}", source_id=f"pricing-{code}-{i}", excerpt=f"{row.provider_name}: negotiated rate {row.negotiated_rate} ({row.negotiated_type or 'type not specified'}).", effective_date=row.file_last_updated) for i, row in enumerate(observations, 1)]
    return AssistantDecision(status="evidence_found", summary=f"Found {len(observations)} public negotiated-rate observation(s) for CPT {code}. These are reference rates, not a member out-of-pocket estimate.", prior_auth_status="unknown", confidence=0.7, evidence=evidence, warnings=["Public negotiated rates are not member-specific out-of-pocket costs.", "Eligibility, network status, deductible, copay, coinsurance, and claim adjudication can change member cost."], recommended_next_steps=["Verify the member plan and network status before estimating out-of-pocket cost.", "Use authorized benefit and eligibility systems for a member-specific estimate."])


def _unavailable_response(summary: str | None = None) -> AssistantDecision:
    return AssistantDecision(status="human_review_required", summary=summary or "Validated negotiated-rate data is not available for this question.", prior_auth_status="unknown", confidence=0.3, warnings=["Do not invent provider prices or member out-of-pocket costs."], recommended_next_steps=["Load a normalized machine-readable pricing file for billing-code lookup.", "Verify member benefits before estimating out-of-pocket cost."])
