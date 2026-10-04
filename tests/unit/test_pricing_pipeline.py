from pathlib import Path

from elevance_ai.agents.provider_cost_agent import build_provider_cost_response
from elevance_ai.ingestion.anthem_mrf import normalize_mrf_to_csv


def test_mrf_normalization_and_cost_agent(tmp_path: Path) -> None:
    output = tmp_path / "pricing.csv"
    count = normalize_mrf_to_csv("tests/fixtures/pricing_mrf.json", output)
    assert count == 1
    decision = build_provider_cost_response("What is the negotiated rate for CPT 99213?", pricing_path=output)
    assert decision.status == "evidence_found"
    assert decision.evidence
    assert "out-of-pocket" in decision.summary


def test_cost_agent_abstains_without_billing_code(tmp_path: Path) -> None:
    decision = build_provider_cost_response("What will this cost me?", pricing_path=tmp_path / "missing.csv")
    assert decision.status == "human_review_required"
    assert decision.confidence < 0.5
