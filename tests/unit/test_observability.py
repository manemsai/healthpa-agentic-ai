from elevance_ai.observability.metrics import record_query, snapshot


def test_metrics_record_only_aggregate_labels() -> None:
    before = snapshot().get("queries_total", 0)
    record_query("policy", "evidence_found")
    current = snapshot()
    assert current["queries_total"] == before + 1
    assert current["route_policy"] >= 1
    assert current["status_evidence_found"] >= 1
