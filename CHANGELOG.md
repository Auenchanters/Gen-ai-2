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
- Unit tests for the generator, features, and risk core.

[Unreleased]: https://github.com/Auenchanters/Gen-ai-2
