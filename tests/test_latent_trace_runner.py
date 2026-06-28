from backend.latency_profiler import LatencyProfiler
from backend.latent_trace_runner import LatentTraceRunner


async def test_latent_trace_runner_uses_actions():
    result = await LatentTraceRunner().run("Compare support and security evidence", 2, 3, LatencyProfiler())
    assert result["trace"]["mode"] == "latent_trace"
    assert result["trace"]["steps"][0]["action"]["intent"] in {"compare_entities", "collect_grounding_evidence"}
