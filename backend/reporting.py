from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from . import database


RESULTS = Path("results")


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


async def write_reports(summary: dict[str, Any], trace_sample: dict[str, Any] | None = None) -> None:
    RESULTS.mkdir(exist_ok=True)
    write_json(RESULTS / "latest_eval_run.json", summary)
    write_json(RESULTS / "retrieval_trace_sample.json", trace_sample or {})
    write_json(RESULTS / "stage_latency_report.json", summary.get("latency_by_stage", {}))
    write_json(RESULTS / "trajectory_quality_report.json", summary.get("metrics", {}))
    write_json(RESULTS / "embedding_diagnostics.json", summary.get("embedding_diagnostics", {}))
    (RESULTS / "latest_eval_summary.md").write_text(_summary_md(summary), encoding="utf-8")
    (RESULTS / "agentic_overhead_report.md").write_text(
        f"# Agentic Overhead Report\n\nAgentic overhead ratio: {summary.get('agentic_overhead_ratio', 1.0)}\n",
        encoding="utf-8",
    )
    failures = await database.fetch_all("SELECT failure_type, details, created_at FROM failure_cases ORDER BY id DESC LIMIT 200")
    with (RESULTS / "failure_cases.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["failure_type", "details", "created_at"])
        writer.writeheader()
        writer.writerows(failures)


def _summary_md(summary: dict[str, Any]) -> str:
    return (
        "# Latest Evaluation Summary\n\n"
        f"Mode: {summary.get('mode', 'mixed')}\n\n"
        f"Cases: {summary.get('case_count', 0)}\n\n"
        f"Grounding score: {summary.get('metrics', {}).get('grounding_score', 0)}\n\n"
        f"Efficiency adjusted score: {summary.get('metrics', {}).get('efficiency_adjusted_score', 0)}\n"
    )
