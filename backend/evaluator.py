from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .efficiency_metrics import efficiency_adjusted_score


FAILURE_TYPES = {
    "empty_retrieval",
    "wrong_source",
    "partial_source_coverage",
    "unsupported_answer",
    "low_overlap",
    "model_unavailable",
    "ambiguous_question",
    "redundant_retrieval",
    "missed_retrieval",
    "early_stop_failure",
    "excessive_latency",
    "citation_missing",
    "citation_irrelevant",
}


def word_set(text: str) -> set[str]:
    return {token.strip(".,:;()[]").lower() for token in text.split() if len(token.strip(".,:;()[]")) > 2}


def overlap_score(answer: str, expected: str) -> float:
    expected_words = word_set(expected)
    if not expected_words:
        return 1.0
    return round(len(word_set(answer) & expected_words) / len(expected_words), 4)


def evaluate_answer(answer: str, citations: list[dict[str, Any]], expected_answer: str, expected_sources: list[str]) -> dict[str, Any]:
    cited_titles = {str(c.get("title", "")).lower() for c in citations}
    expected = {source.lower() for source in expected_sources}
    citation_hits = sum(1 for source in expected if any(source in title or title in source for title in cited_titles))
    precision = citation_hits / max(1, len(cited_titles))
    recall = citation_hits / max(1, len(expected))
    overlap = overlap_score(answer, expected_answer)
    grounding = round((overlap + recall) / 2, 4)
    failures: list[str] = []
    if not citations:
        failures.append("empty_retrieval")
    if recall == 0 and expected:
        failures.append("wrong_source")
    elif recall < 1 and expected:
        failures.append("partial_source_coverage")
    if overlap < 0.25:
        failures.append("low_overlap")
    if precision == 0 and cited_titles:
        failures.append("citation_irrelevant")
    return {
        "retrieval_hit_rate": round(recall, 4),
        "retrieval_success_rate": 1.0 if recall > 0 else 0.0,
        "source_coverage": round(recall, 4),
        "answer_overlap_score": overlap,
        "grounding_score": grounding,
        "citation_recall": round(recall, 4),
        "citation_precision": round(precision, 4),
        "missing_source_count": max(0, len(expected) - citation_hits),
        "empty_retrieval_count": 0 if citations else 1,
        "unsupported_answer_flag": grounding < 0.25,
        "failure_types": failures,
    }


def load_eval_cases(path: Path = Path("corpus/evaluation/eval_cases.jsonl")) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def summarize_metrics(items: list[dict[str, Any]], total_latency_ms: float = 0.0) -> dict[str, Any]:
    if not items:
        return {}
    keys = ["retrieval_hit_rate", "source_coverage", "answer_overlap_score", "grounding_score", "citation_recall", "citation_precision"]
    summary = {key: round(sum(float(item.get(key, 0.0)) for item in items) / len(items), 4) for key in keys}
    quality = (summary["grounding_score"] + summary["citation_recall"] + summary["answer_overlap_score"]) / 3
    summary["efficiency_adjusted_score"] = efficiency_adjusted_score(quality, total_latency_ms or 1.0)
    return summary
