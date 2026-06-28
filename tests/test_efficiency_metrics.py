from backend.efficiency_metrics import agentic_overhead_ratio, efficiency_adjusted_score


def test_efficiency_metrics_safe_defaults():
    assert agentic_overhead_ratio(200, 100) == 2.0
    assert efficiency_adjusted_score(0.8, 100) > 0
