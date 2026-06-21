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
- Backend API (`server/`):
  - FastAPI app serving `/api/health`, `/api/forecast`, `/api/risk`, `/api/alerts`,
    and `/api/ask`, with security headers, CORS, and a static-frontend mount point.
  - Layered repository behind a `Protocol`: local parquet (with zero-setup demo
    generation) and a BigQuery implementation, selected by the `USE_BIGQUERY` flag.
  - Gemini-backed natural-language answers (`USE_GEMINI`) with a deterministic,
    data-grounded rules fallback; every answer source-tagged.
  - Typed Pydantic request/response models with input bounds.
- Frontend (`web/`): accessible React + TypeScript dashboard (Vite) — risk ranking,
  demand-vs-capacity forecast chart, alerts, and a natural-language ask box. Every chart
  has a data-table equivalent; types mirror the backend schemas.
- Unit + integration tests across pipeline, server, and web (49 tests: 44 backend +
  5 frontend, with Vitest + axe-core a11y assertions).

### Changed

- Added `xgboost`, `fastapi`, `uvicorn`, `pydantic`, `pydantic-settings` dependencies and
  an optional `cloud` extra (BigQuery + google-genai). Notebooks excluded from ruff.
- Added a second CI job for the frontend (ESLint + jsx-a11y, strict tsc, Vitest coverage,
  production build).

[Unreleased]: https://github.com/Auenchanters/Gen-ai-2
