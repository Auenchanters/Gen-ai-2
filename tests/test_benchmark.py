"""Tests for the benchmark harness (CPU path) and its result aggregation."""

import json

from pipeline import benchmark


def test_run_once_returns_timed_record():
    record = benchmark.run_once(meters_per_zone=5, days=1, zones=2)
    assert record.engine == "cpu"
    assert record.rows == 2 * 5 * 1 * 48
    assert record.pipeline_seconds > 0
    assert record.rows_per_sec > 0


def test_save_dedupes_and_summarize_computes_speedup(tmp_path):
    out = tmp_path / "results.json"
    benchmark.save_result(benchmark.BenchRecord("cpu", 1000, 8, 2.0, 500), out)
    benchmark.save_result(
        benchmark.BenchRecord("cpu", 1000, 8, 1.8, 555), out
    )  # replaces prior cpu
    benchmark.save_result(benchmark.BenchRecord("gpu", 1000, 8, 0.18, 5555), out)

    records = json.loads(out.read_text())
    assert sum(1 for r in records if r["engine"] == "cpu") == 1  # deduped

    summary = benchmark.summarize(records)
    assert len(summary) == 1
    assert summary[0]["rows"] == 1000
    assert summary[0]["speedup"] == 10.0  # 1.8 / 0.18
