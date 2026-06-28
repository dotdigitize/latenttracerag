from __future__ import annotations

import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Iterator


STAGES = [
    "prefill_time_ms",
    "thought_generation_time_ms",
    "subquery_generation_time_ms",
    "retrieval_time_ms",
    "answer_generation_time_ms",
]


@dataclass
class LatencyProfiler:
    stages: dict[str, float] = field(default_factory=lambda: {stage: 0.0 for stage in STAGES})
    started_at: float = field(default_factory=time.perf_counter)

    @contextmanager
    def stage(self, name: str) -> Iterator[None]:
        start = time.perf_counter()
        try:
            yield
        finally:
            self.stages[name] = self.stages.get(name, 0.0) + (time.perf_counter() - start) * 1000

    def add_estimate(self, name: str, value_ms: float) -> None:
        self.stages[name] = self.stages.get(name, 0.0) + max(0.0, value_ms)

    def snapshot(self) -> dict[str, float]:
        total = (time.perf_counter() - self.started_at) * 1000
        data = {stage: round(self.stages.get(stage, 0.0), 3) for stage in STAGES}
        data["total_time_ms"] = round(max(total, sum(data.values())), 3)
        return data
