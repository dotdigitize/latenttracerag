from backend.agentic_runner import AgenticRunner
from backend.latency_profiler import LatencyProfiler


async def test_agentic_runner_fallback_answers():
    result = await AgenticRunner().run_agentic("What approval is required for large payments?", 2, 2, LatencyProfiler())
    assert result["answer"]
    assert result["trace"]["mode"] == "agentic"
    assert len(result["trace"]["steps"]) == 2
