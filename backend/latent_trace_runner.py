from __future__ import annotations

import re
import time
from typing import Any

from .agentic_runner import citations_from_chunks, extractive_answer
from .latency_profiler import LatencyProfiler
from .ollama_client import OllamaClient
from .retriever import RetrievedChunk, Retriever


class LatentTraceRunner:
    def __init__(self, retriever: Retriever | None = None, client: OllamaClient | None = None) -> None:
        self.client = client or OllamaClient()
        self.retriever = retriever or Retriever(self.client)

    async def run(self, query: str, top_k: int, max_steps: int, profiler: LatencyProfiler) -> dict[str, Any]:
        model_unavailable = not await self.client.available()
        with profiler.stage("thought_generation_time_ms"):
            actions = self._actions_for_query(query, max_steps)
        all_chunks: list[RetrievedChunk] = []
        steps: list[dict[str, Any]] = []
        for index, action in enumerate(actions, start=1):
            with profiler.stage("subquery_generation_time_ms"):
                subqueries = self._subqueries_from_action(action)
            retrieved_ids: list[int] = []
            start = time.perf_counter()
            for subquery in subqueries:
                with profiler.stage("retrieval_time_ms"):
                    chunks = await self.retriever.retrieve(subquery, top_k)
                all_chunks.extend(chunks)
                retrieved_ids.extend(chunk.chunk_id for chunk in chunks)
            steps.append(
                {
                    "step_index": index,
                    "action": action,
                    "decoded_trace": self.decode_action(action),
                    "subquery": " | ".join(subqueries),
                    "retrieved_chunk_ids": sorted(set(retrieved_ids)),
                    "latency_ms": round((time.perf_counter() - start) * 1000, 3),
                }
            )
        deduped = self._dedupe(all_chunks)
        with profiler.stage("answer_generation_time_ms"):
            generated = None if model_unavailable else await self.client.generate(self._answer_prompt(query, deduped, steps))
            answer = generated or extractive_answer(query, deduped)
        return {
            "answer": answer,
            "citations": citations_from_chunks(deduped),
            "trace": {"mode": "latent_trace", "steps": steps, "decoded_summary": [step["decoded_trace"] for step in steps]},
            "model_unavailable": model_unavailable,
        }

    def _actions_for_query(self, query: str, max_steps: int) -> list[dict[str, Any]]:
        entities = [part.strip(" ?.,") for part in re.split(r"\band\b|,|;", query) if len(part.strip()) > 4][:4]
        action = {
            "intent": "collect_grounding_evidence",
            "target": self._target(query),
            "entities": entities or [query],
            "needed_evidence": ["source statement", "policy or operational detail", "citation support"],
        }
        if any(word in query.lower() for word in ["compare", "difference", "versus", "vs"]):
            action["intent"] = "compare_entities"
        return [action][: max(1, max_steps)]

    @staticmethod
    def _target(query: str) -> str:
        lowered = query.lower()
        for word in ["latency", "risk", "policy", "security", "release", "support", "contract", "medical"]:
            if word in lowered:
                return word
        return "answer evidence"

    @staticmethod
    def _subqueries_from_action(action: dict[str, Any]) -> list[str]:
        target = action.get("target", "evidence")
        return [f"{entity} {target} {need}" for entity in action.get("entities", []) for need in action.get("needed_evidence", [])][:4]

    @staticmethod
    def decode_action(action: dict[str, Any]) -> str:
        entities = ", ".join(action.get("entities", []))
        return f"{action.get('intent')} for {entities} targeting {action.get('target')}."

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
    def _answer_prompt(query: str, chunks: list[RetrievedChunk], steps: list[dict[str, Any]]) -> str:
        evidence = "\n".join(f"[{chunk.title}] {chunk.text}" for chunk in chunks)
        return f"Use the compact retrieval trace and evidence to answer.\nQuery: {query}\nTrace: {steps}\nEvidence:\n{evidence}"
