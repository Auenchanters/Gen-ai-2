# GridPulse — Accelerated Energy Demand & Peak-Risk Intelligence

[![CI](https://github.com/Auenchanters/Gen-ai-2/actions/workflows/ci.yml/badge.svg)](https://github.com/Auenchanters/Gen-ai-2/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](pyproject.toml)

> **A data-intelligence tool a grid operator would actually use** — it forecasts the
> next 24–48 h of electricity demand per zone, scores peak-overload risk, and recommends
> action, turning millions of smart-meter readings into a decision in **seconds** by
> running the heavy data work on an **NVIDIA GPU** with RAPIDS `cudf.pandas`.

GridPulse is a submission for **Problem Statement 2**: build a practical data analytics /
decision-support tool, and show how **acceleration** helps a real user make a **faster,
better decision**.

> **Status:** under active development. This README documents the target system and is
> kept in sync with what is implemented. See the [rubric-to-repo map](#rubric-to-repo-map)
> for what is live today.

## Who uses this, and what decision does it accelerate?

**User:** an operations / load planner at a regional electricity distributor (the same
shape fits a campus or community-microgrid energy manager).

**The daily decision:** *Where and when will demand peak in the next 24–48 h, which zones
are at risk of overload/outage, and what do I do about it* — procure more power, request
load-shifting, or pre-position crews?

**The bottleneck:** the answer lives in millions of half-hourly smart-meter readings plus
weather. Cleaning, aggregating, and modelling that on a CPU is slow enough that the
insight arrives too late to act on.

**How acceleration helps:** GPU-accelerated dataframes (RAPIDS `cudf.pandas`) and ML
(`cuML` / XGBoost-GPU) crunch the same data in seconds, so the planner gets the forecast,
risk ranking, and recommendations in time — and can ask follow-up questions in plain
English (Gemini).

## What it produces

Forecast (24–48 h demand curve per zone) · per-zone peak-risk **score** · **alerts** for
high-risk windows · **ranking** of zones by risk · **recommendations** (rules + Gemini
narration) · natural-language **Q&A** over the results.

## Architecture

```
 Synthetic generator OR real dataset (London Smart Meters / ASHRAE)
        │  parquet
        ▼
   Cloud Storage ──►  [OFFLINE BATCH, GPU]  pipeline/
        │               cudf.pandas clean + aggregate + features
        │               → cuML / XGBoost-GPU forecast + risk
        │               benchmark.py: CPU pandas vs GPU cuDF → benchmarks/results.json
        ▼                         │
     BigQuery  ◄──────────────────┘  forecasts + risk tables  (local parquet fallback)
        ▲
        │ read (no GPU)
   [ONLINE]  server/ FastAPI ── Gemini (Vertex AI): NL Q&A + recommendations (rules fallback)
        │
   web/ React + TS dashboard ── charts, risk ranking, alerts, NL query
        └──────────────────────────── all served from one Cloud Run container ───────────┘
```

**Key design decision:** the GPU is used only in the offline batch/benchmark step (run on
a free Colab/Kaggle T4 plus one short GCP L4 run); results are written to BigQuery. The
**live app needs no GPU** and runs on Cloud Run (scale-to-zero), so running costs stay
near zero while the acceleration evidence is real and recorded.

## Technology

**Google Cloud:** BigQuery · Cloud Storage · Cloud Run · Vertex AI (Gemini) · (Looker
Studio dashboard, optional).
**NVIDIA acceleration:** RAPIDS `cudf.pandas` · `cuML` / XGBoost-GPU · NVIDIA GPU on
Google Cloud.

## Quickstart

```bash
uv sync --extra dev                     # Python 3.11 env + deps
uv run python -m pipeline.generate_data --days 7 --meters-per-zone 200   # writes data/
uv run pytest                           # tests + coverage gate
```

Everything runs on CPU with **no GPU and no cloud credentials**. GPU acceleration and
the cloud integrations switch on via environment flags (`USE_GPU`, `USE_BIGQUERY`,
`USE_GEMINI`); see [.env.example](.env.example).

## Acceleration evidence

The CPU-vs-GPU benchmark (`pipeline/benchmark.py`, lands in P2) records wall-time,
rows/sec, and speedup across data scales into `benchmarks/results.json`.

| Rows | CPU pandas | GPU cudf.pandas | Speedup |
| ---- | ---------- | --------------- | ------- |
| _to be filled by `benchmark.py`_ | | | |

## Testing

| Layer | Tooling | What it covers |
| ----- | ------- | -------------- |
| Pure core | pytest + coverage gate | generator determinism, feature correctness, risk scoring |
| Static | mypy `--strict`, ruff | types and lint across `pipeline/` and `tests/` |
| API / frontend | (P3 / P4) | integration tests with fakes, a11y assertions |

## Rubric-to-repo map

How this submission satisfies Problem Statement 2:

| Brief requirement | Where it lives | Status |
| ----------------- | -------------- | ------ |
| Clear real-world user & problem | [Who uses this](#who-uses-this-and-what-decision-does-it-accelerate) | ✅ |
| Specific data-dependent decision | daily peak / risk / action decision | ✅ |
| Pipeline: ingest → clean → analyze → model → visualize | `pipeline/` → `server/` → `web/` | 🚧 |
| Useful output (forecast / risk / alert / ranking / recommendation) | `pipeline/risk.py`, dashboard | 🚧 |
| Evidence acceleration improves the experience | `pipeline/benchmark.py`, [table](#acceleration-evidence) | 🚧 |
| ≥1 Google Cloud service | BigQuery, Cloud Storage, Cloud Run, Vertex AI | 🚧 |
| ≥1 NVIDIA acceleration tech | `cudf.pandas`, `cuML`, GPU on GCP | 🚧 |

## License

[MIT](LICENSE).
