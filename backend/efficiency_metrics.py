from __future__ import annotations

import math
from typing import Any


def agentic_overhead_ratio(agentic_total_latency: float, naive_total_latency: float | None) -> float:
    baseline = naive_total_latency if naive_total_latency and naive_total_latency > 0 else agentic_total_latency or 1.0
    return round((agentic_total_latency or 0.0) / baseline, 4)


def efficiency_adjusted_score(weighted_quality_score: float, total_latency_ms: float) -> float:
    return round(weighted_quality_score / math.log1p(max(total_latency_ms, 1.0)), 4)


def token_estimate_by_stage(trace: dict[str, Any]) -> dict[str, int]:
    steps = trace.get("steps", [])
    thought_tokens = sum(len(str(step.get("thought", "")).split()) for step in steps)
    subquery_tokens = sum(len(str(step.get("subquery", "")).split()) for step in steps)
    action_tokens = sum(len(str(step.get("action", "")).split()) for step in steps)
    answer_tokens = len(str(trace.get("answer", "")).split())
    return {
        "thought_generation": thought_tokens,
        "subquery_generation": subquery_tokens + action_tokens,
        "answer_generation": answer_tokens,
    }
