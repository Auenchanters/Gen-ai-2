# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Project scaffold: `pyproject.toml`, ruff + mypy (strict) + pytest config, pre-commit
  hooks, and a GitHub Actions CI pipeline with enforced lint/format/type/coverage gates.
- Pure data pipeline core:
  - `pipeline/generate_data.py` — deterministic, scalable synthetic smart-meter + weather
    generator.
  - `pipeline/engine.py` — CPU pandas / GPU `cudf.pandas` engine selection with CPU
    fallback.
  - `pipeline/features.py` — pure feature engineering (zone aggregation, calendar,
    weather join, leakage-free lags).
  - `pipeline/risk.py` — pure peak-overload risk scoring, banding, and rule-based
    recommendations.
- Acceleration layer:
  - `pipeline/accelerate.py` — batch pipeline that enables RAPIDS `cudf.pandas` (GPU)
    when `USE_GPU=1`, with automatic CPU fallback.
  - `pipeline/train.py` — XGBoost demand-forecasting model (native API; CPU/GPU from one
    `device` parameter) and the serving forecast + risk table.
  - `pipeline/benchmark.py` — CPU-vs-GPU timing harness writing `benchmarks/results.json`;
    `notebooks/benchmark_colab.ipynb` + `docs/BENCHMARK.md` for the GPU run.
  - CPU baseline recorded: 23.0M rows through the pipeline in 1.36 s.
- Unit tests for the generator, features, risk, pipeline, model, and benchmark
  (23 tests, ~99% pipeline coverage).

### Changed

- Added `xgboost` runtime dependency; notebooks excluded from ruff.

[Unreleased]: https://github.com/Auenchanters/Gen-ai-2
