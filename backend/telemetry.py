from __future__ import annotations

import json
from typing import Any

from . import database


async def record_latency(query_id: int | None, stages: dict[str, float]) -> None:
    await database.execute(
        "INSERT INTO latency_traces (query_id, stage_json, total_time_ms) VALUES (?, ?, ?)",
        (query_id, json.dumps(stages), float(stages.get("total_time_ms", 0.0))),
    )


async def record_trajectory(query_id: int | None, metrics: dict[str, Any]) -> None:
    await database.execute(
        "INSERT INTO trajectory_metrics (query_id, metrics_json) VALUES (?, ?)",
        (query_id, json.dumps(metrics, sort_keys=True)),
    )
