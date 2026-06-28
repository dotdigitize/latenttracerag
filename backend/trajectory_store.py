from __future__ import annotations

import json
from typing import Any

from . import database


async def create_query(query_text: str, mode: str, top_k: int, max_retrieval_steps: int, case_id: str | None = None) -> int:
    return await database.execute(
        "INSERT INTO queries (query_text, mode, top_k, max_retrieval_steps, case_id) VALUES (?, ?, ?, ?, ?)",
        (query_text, mode, top_k, max_retrieval_steps, case_id),
    )


async def store_trace(query_id: int, mode: str, trace: dict[str, Any], model_unavailable: bool) -> int:
    trace_id = await database.execute(
        "INSERT INTO retrieval_traces (query_id, mode, model_unavailable, trace_json) VALUES (?, ?, ?, ?)",
        (query_id, mode, int(model_unavailable), json.dumps(trace, sort_keys=True)),
    )
    for step in trace.get("steps", []):
        await database.execute(
            """
            INSERT INTO retrieval_steps
            (trace_id, step_index, thought, subquery, action_json, retrieved_chunk_ids, latency_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                trace_id,
                int(step.get("step_index", 0)),
                step.get("thought"),
                step.get("subquery"),
                json.dumps(step.get("action")) if step.get("action") is not None else None,
                json.dumps(step.get("retrieved_chunk_ids", [])),
                float(step.get("latency_ms", 0.0)),
            ),
        )
    return trace_id


async def store_answer(query_id: int, answer: str, citations: list[dict[str, Any]], metrics: dict[str, Any]) -> int:
    return await database.execute(
        "INSERT INTO answers (query_id, answer_text, citations_json, metrics_json) VALUES (?, ?, ?, ?)",
        (query_id, answer, json.dumps(citations), json.dumps(metrics, sort_keys=True)),
    )


async def get_query_trace(query_id: int) -> dict[str, Any] | None:
    query = await database.fetch_one("SELECT * FROM queries WHERE id = ?", (query_id,))
    trace = await database.fetch_one("SELECT * FROM retrieval_traces WHERE query_id = ? ORDER BY id DESC LIMIT 1", (query_id,))
    answer = await database.fetch_one("SELECT * FROM answers WHERE query_id = ? ORDER BY id DESC LIMIT 1", (query_id,))
    if not query or not trace:
        return None
    return {
        "query": query,
        "trace": json.loads(trace["trace_json"]),
        "model_unavailable": bool(trace["model_unavailable"]),
        "answer": json.loads(answer["metrics_json"]) | {"text": answer["answer_text"], "citations": json.loads(answer["citations_json"])}
        if answer
        else None,
    }
