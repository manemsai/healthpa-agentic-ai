from elevance_ai.agents.policy_agent import build_decision


def test_empty_evidence_never_claims_authorization() -> None:
    decision = build_decision([])
    assert decision.prior_auth_status == "no_public_evidence_found"
    assert decision.confidence < 0.5
    assert "approved" not in decision.summary.lower()
    assert "denied" not in decision.summary.lower()
