from __future__ import annotations

import json
from typing import Any, Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from . import database
from .agentic_runner import AgenticRunner
from .config import settings
from .document_store import get_document, list_documents, seed_reference_corpus
from .efficiency_metrics import agentic_overhead_ratio, token_estimate_by_stage
from .embedding_diagnostics import compute_embedding_diagnostics
from .evaluator import evaluate_answer, load_eval_cases, summarize_metrics
from .latency_profiler import LatencyProfiler
from .latent_trace_runner import LatentTraceRunner
from .ollama_client import OllamaClient
from .reporting import write_reports
from .telemetry import record_latency, record_trajectory
from .trajectory_store import create_query, get_query_trace, store_answer, store_trace

app = FastAPI(title="LatentTraceRAG", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


class QueryRequest(BaseModel):
    query_text: str = Field(min_length=1)
    mode: Literal["naive", "agentic", "latent_trace"] = "latent_trace"
    top_k: int = Field(default=settings.top_k, ge=1, le=10)
    max_retrieval_steps: int = Field(default=settings.max_retrieval_steps, ge=1, le=8)
    case_id: str | None = None


@app.on_event("startup")
async def startup() -> None:
    await database.init_db()


@app.get("/health")
async def health() -> dict[str, Any]:
    return {"status": "ok", "database": str(settings.database_path), "external_apis_allowed": settings.allow_external_apis}


@app.get("/models")
async def models() -> dict[str, Any]:
    client = OllamaClient()
    return {
        "configured": {
            "ollama_base_url": settings.ollama_base_url,
            "chat_model": settings.chat_model,
            "worker_model": settings.worker_model,
            "embed_model": settings.embed_model,
            "database_path": str(settings.database_path),
            "top_k": settings.top_k,
            "max_retrieval_steps": settings.max_retrieval_steps,
            "allow_external_apis": settings.allow_external_apis,
        },
        "available_models": await client.list_models(),
    }


@app.post("/api/seed")
async def seed_api() -> dict[str, Any]:
    count = await seed_reference_corpus()
    diagnostics = await compute_embedding_diagnostics()
    return {"documents_seeded": count, "embedding_diagnostics": diagnostics}


@app.get("/api/documents")
async def documents() -> list[dict[str, Any]]:
    return await list_documents()


@app.get("/api/documents/{document_id}")
async def document(document_id: int) -> dict[str, Any]:
    item = await get_document(document_id)
    if not item:
        raise HTTPException(status_code=404, detail="Document not found")
    return item


@app.post("/api/query")
async def query_api(request: QueryRequest) -> dict[str, Any]:
    query_id = await create_query(request.query_text, request.mode, request.top_k, request.max_retrieval_steps, request.case_id)
    profiler = LatencyProfiler()
    profiler.add_estimate("prefill_time_ms", 1.0)
    agentic = AgenticRunner()
    if request.mode == "naive":
        result = await agentic.run_naive(request.query_text, request.top_k, profiler)
    elif request.mode == "agentic":
        result = await agentic.run_agentic(request.query_text, request.top_k, request.max_retrieval_steps, profiler)
    else:
        result = await LatentTraceRunner().run(request.query_text, request.top_k, request.max_retrieval_steps, profiler)
    stages = profiler.snapshot()
    metrics = _default_metrics(result, stages)
    trace = result["trace"] | {"answer": result["answer"], "latency_by_stage": stages, "token_estimate_by_stage": token_estimate_by_stage(result["trace"])}
    await store_trace(query_id, request.mode, trace, result["model_unavailable"])
    await store_answer(query_id, result["answer"], result["citations"], metrics)
    await record_latency(query_id, stages)
    await record_trajectory(query_id, metrics)
    return {"query_id": query_id, "answer": result["answer"], "citations": result["citations"], "trace": trace, "metrics": metrics, "model_unavailable": result["model_unavailable"]}


@app.get("/api/query/{query_id}/trace")
async def trace_api(query_id: int) -> dict[str, Any]:
    trace = await get_query_trace(query_id)
    if not trace:
        raise HTTPException(status_code=404, detail="Trace not found")
    return trace


@app.post("/api/evals/run")
async def run_evals(mode: Literal["naive", "agentic", "latent_trace"] = "latent_trace") -> dict[str, Any]:
    cases = load_eval_cases()
    metrics: list[dict[str, Any]] = []
    trace_sample: dict[str, Any] | None = None
    total_latency = 0.0
    for case in cases:
        response = await query_api(QueryRequest(query_text=case["question"], mode=mode, case_id=case["id"]))
        item_metrics = evaluate_answer(response["answer"], response["citations"], case["expected_answer"], case["expected_sources"])
        metrics.append(item_metrics)
        total_latency += response["trace"]["latency_by_stage"]["total_time_ms"]
        trace_sample = trace_sample or response["trace"]
    summary_metrics = summarize_metrics(metrics, total_latency)
    summary = {
        "mode": mode,
        "case_count": len(cases),
        "metrics": summary_metrics,
        "latency_by_stage": {"total_time_ms": round(total_latency, 3)},
        "agentic_overhead_ratio": agentic_overhead_ratio(total_latency, total_latency if mode == "naive" else None),
        "embedding_diagnostics": await compute_embedding_diagnostics(),
    }
    run_id = await database.execute("INSERT INTO evaluation_runs (mode, summary_json) VALUES (?, ?)", (mode, json.dumps(summary)))
    summary["run_id"] = run_id
    await write_reports(summary, trace_sample)
    return summary


@app.get("/api/evals/runs")
async def eval_runs() -> list[dict[str, Any]]:
    return await database.fetch_all("SELECT id, mode, summary_json, created_at FROM evaluation_runs ORDER BY id DESC")


@app.get("/api/evals/runs/{run_id}")
async def eval_run(run_id: int) -> dict[str, Any]:
    row = await database.fetch_one("SELECT * FROM evaluation_runs WHERE id = ?", (run_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Evaluation run not found")
    row["summary"] = json.loads(row["summary_json"])
    return row


@app.get("/api/failures")
async def failures() -> list[dict[str, Any]]:
    return await database.fetch_all("SELECT * FROM failure_cases ORDER BY id DESC LIMIT 200")


@app.get("/api/reports/latest")
async def latest_report() -> dict[str, Any]:
    row = await database.fetch_one("SELECT * FROM evaluation_runs ORDER BY id DESC LIMIT 1")
    return {"summary": json.loads(row["summary_json"]) if row else {}, "path": "results/latest_eval_summary.md"}


@app.get("/api/latency/latest")
async def latest_latency() -> dict[str, Any]:
    row = await database.fetch_one("SELECT * FROM latency_traces ORDER BY id DESC LIMIT 1")
    return json.loads(row["stage_json"]) if row else {}


@app.get("/api/diagnostics/embeddings")
async def embedding_diag() -> dict[str, Any]:
    return await compute_embedding_diagnostics()


@app.get("/api/config")
async def config_api() -> dict[str, Any]:
    return {"chat_model": settings.chat_model, "worker_model": settings.worker_model, "embed_model": settings.embed_model, "top_k": settings.top_k, "max_retrieval_steps": settings.max_retrieval_steps, "allow_external_apis": settings.allow_external_apis}


def _default_metrics(result: dict[str, Any], stages: dict[str, float]) -> dict[str, Any]:
    redundant = 0.0
    ids: list[int] = []
    for step in result["trace"].get("steps", []):
        ids.extend(step.get("retrieved_chunk_ids", []))
    if ids:
        redundant = 1.0 - (len(set(ids)) / len(ids))
    return {
        "grounding_score": 1.0 if result["citations"] else 0.0,
        "citation_recall": 1.0 if result["citations"] else 0.0,
        "citation_precision": 1.0 if result["citations"] else 0.0,
        "redundant_retrieval_rate": round(redundant, 4),
        "empty_retrieval_count": 0 if result["citations"] else 1,
        "unsupported_answer_flag": not bool(result["citations"]),
        "model_unavailable": result["model_unavailable"],
        "latency_by_stage": stages,
    }
