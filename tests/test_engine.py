"""Tests for CPU/GPU engine selection (the CPU fallback path that runs in CI)."""

from pipeline import engine


def test_gpu_unavailable_without_rapids():
    assert engine.gpu_available() is False


def test_maybe_enable_returns_false_without_flag(monkeypatch):
    monkeypatch.delenv("USE_GPU", raising=False)
    assert engine.maybe_enable_cudf_pandas() is False
