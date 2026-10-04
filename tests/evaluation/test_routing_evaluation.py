from scripts.evaluate import evaluate


def test_evaluation_gate_passes() -> None:
    result = evaluate()
    assert result["routing_accuracy"] == 1.0
    assert result["safe_abstention"] is True
    assert result["passed"] is True
