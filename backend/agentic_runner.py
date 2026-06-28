from __future__ import annotations

import time
from typing import Any

from .latency_profiler import LatencyProfiler
from .ollama_client import OllamaClient
from .retriever import RetrievedChunk, Retriever


def extractive_answer(query: str, chunks: list[RetrievedChunk]) -> str:
    if not chunks:
        return "No supporting evidence was retrieved for this query."
    sentence = chunks[0].text.split(".")[0].strip()
    return f"{sentence}. Evidence was retrieved from {chunks[0].title}."


def citations_from_chunks(chunks: list[RetrievedChunk]) -> list[dict[str, Any]]:
    seen: set[int] = set()
    citations: list[dict[str, Any]] = []
    for chunk in chunks:
        if chunk.chunk_id in seen:
            continue
        seen.add(chunk.chunk_id)
        citations.append({"chunk_id": chunk.chunk_id, "document_id": chunk.document_id, "title": chunk.title, "score": chunk.score})
    return citations


class AgenticRunner:
    def __init__(self, retriever: Retriever | None = None, client: OllamaClient | None = None) -> None:
        self.client = client or OllamaClient()
        self.retriever = retriever or Retriever(self.client)

    async def run_naive(self, query: str, top_k: int, profiler: LatencyProfiler) -> dict[str, Any]:
        with profiler.stage("retrieval_time_ms"):
            start = time.perf_counter()
            chunks = await self.retriever.retrieve(query, top_k)
        model_unavailable = not await self.client.available()
        with profiler.stage("answer_generation_time_ms"):
            generated = None if model_unavailable else await self.client.generate(self._answer_prompt(query, chunks))
            answer = generated or extractive_answer(query, chunks)
        return {
            "answer": answer,
            "citations": citations_from_chunks(chunks),
            "trace": {
                "mode": "naive",
                "steps": [
                    {
                        "step_index": 1,
                        "thought": None,
                        "subquery": query,
                        "retrieved_chunk_ids": [chunk.chunk_id for chunk in chunks],
                        "latency_ms": round((time.perf_counter() - start) * 1000, 3),
                    }
                ],
            },
            "model_unavailable": model_unavailable,
        }

    async def run_agentic(self, query: str, top_k: int, max_steps: int, profiler: LatencyProfiler) -> dict[str, Any]:
        model_unavailable = not await self.client.available()
        all_chunks: list[RetrievedChunk] = []
        steps: list[dict[str, Any]] = []
        subqueries = self._fallback_subqueries(query, max_steps)
        for index, subquery in enumerate(subqueries, start=1):
            with profiler.stage("thought_generation_time_ms"):
                thought = (
                    None
                    if model_unavailable
                    else await self.client.generate(f"Write one concise retrieval thought for: {query}", model=None)
                )
                thought = thought or f"Identify evidence needed for retrieval step {index}."
            with profiler.stage("subquery_generation_time_ms"):
                generated_subquery = None if model_unavailable else await self.client.generate(f"Write a search query for: {query}")
                active_subquery = generated_subquery or subquery
            start = time.perf_counter()
            with profiler.stage("retrieval_time_ms"):
                chunks = await self.retriever.retrieve(active_subquery, top_k)
            all_chunks.extend(chunks)
            steps.append(
                {
                    "step_index": index,
                    "thought": thought,
                    "subquery": active_subquery,
                    "retrieved_chunk_ids": [chunk.chunk_id for chunk in chunks],
                    "latency_ms": round((time.perf_counter() - start) * 1000, 3),
                }
            )
        deduped = self._dedupe(all_chunks)
        with profiler.stage("answer_generation_time_ms"):
            generated = None if model_unavailable else await self.client.generate(self._answer_prompt(query, deduped))
            answer = generated or extractive_answer(query, deduped)
        return {
            "answer": answer,
            "citations": citations_from_chunks(deduped),
            "trace": {"mode": "agentic", "steps": steps},
            "model_unavailable": model_unavailable,
        }

    @staticmethod
    def _fallback_subqueries(query: str, max_steps: int) -> list[str]:
        base = [query, f"supporting policy evidence for {query}", f"risk and exception details for {query}", f"final citation evidence for {query}"]
        return base[: max(1, max_steps)]

    @staticmethod
    def _dedupe(chunks: list[RetrievedChunk]) -> list[RetrievedChunk]:
        seen: set[int] = set()
        output: list[RetrievedChunk] = []
        for chunk in chunks:
            if chunk.chunk_id not in seen:
                seen.add(chunk.chunk_id)
                output.append(chunk)
        return output

    @staticmethod
    def _answer_prompt(query: str, chunks: list[RetrievedChunk]) -> str:
        evidence = "\n\n".join(f"[{chunk.title}] {chunk.text}" for chunk in chunks)
        return f"Answer using only the evidence. Query: {query}\nEvidence:\n{evidence}"
