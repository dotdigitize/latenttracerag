from backend.latency_profiler import LatencyProfiler


def test_latency_profiler_records_stage():
    profiler = LatencyProfiler()
    with profiler.stage("retrieval_time_ms"):
        sum(range(10))
    snapshot = profiler.snapshot()
    assert snapshot["retrieval_time_ms"] >= 0
    assert snapshot["total_time_ms"] >= snapshot["retrieval_time_ms"]
