# GridPulse architecture

GridPulse turns millions of smart-meter readings into a next-24–48 h demand forecast,
per-zone peak-overload risk, alerts, and recommendations — fast enough for a grid
operations planner to act on. This document explains how the pieces fit and why.

## The one decision that shapes everything

**GPU offline and recorded; serving online and serverless.**

The GPU does the heavy data work (cleaning, aggregating, feature engineering, model
training) in an *offline batch* step, and the results are written to BigQuery. The *live
app* never needs a GPU — it reads precomputed forecasts and serves them from Cloud Run
(scale-to-zero). This gives real, measurable acceleration evidence while keeping running
cost near zero, and it means a limited GPU budget is enough.

```
 Synthetic generator OR real dataset (London Smart Meters / ASHRAE)
        │  parquet
        ▼
   Cloud Storage ──►  [OFFLINE BATCH, GPU]  pipeline/
        │               cudf.pandas clean + aggregate + features  (engine.py / features.py)
        │               → XGBoost (device="cuda") forecast + risk  (train.py)
        │               benchmark.py: CPU pandas vs GPU cuDF → benchmarks/results.json
        ▼                         │
     BigQuery  ◄──────────────────┘  forecast + risk table   (local parquet fallback)
        ▲
        │ read (no GPU)
   [ONLINE]  server/ FastAPI ── Gemini (Vertex AI) NL Q&A + recommendations (rules fallback)
        │
   web/ React + TypeScript dashboard ── charts + data tables, risk ranking, alerts, ask box
        └────────────────────────── one Cloud Run container (API + built SPA) ───────────┘
```

## Layers (dependencies point inward)

- **Domain (pure, no I/O).** `pipeline/features.py`, `pipeline/risk.py`, and
  `server/domain.py` are deterministic functions over dataframes/values. Same input →
  same output, so they are trivially testable and the API and offline pipeline agree by
  construction (both call `pipeline/risk.py`).
- **Engine abstraction.** `pipeline/engine.py` selects CPU pandas or GPU `cudf.pandas`
  from one flag; the transform code is identical on both.
- **Persistence is an interface.** `server/repository.py` defines a `ForecastRepository`
  `Protocol`. Routes depend on the interface, never a concrete backend, so a fake slots in
  for tests and BigQuery swaps for local parquet via a flag.
- **Service layer.** `server/ai.py` wraps Gemini behind a stable function with a
  deterministic fallback.
- **Transport.** `server/main.py` is thin: validation lives in `server/schemas.py`
  (Pydantic bounds), and it wires middleware, CORS, dependency injection, and the SPA mount.

## Graceful degradation (why it runs anywhere)

Every external dependency is behind a default-off flag with a fallback, and every response
is tagged with the source that produced it:

| Flag | On | Off (fallback) | Tag |
| ---- | -- | -------------- | --- |
| `USE_GPU` | RAPIDS `cudf.pandas` + XGBoost CUDA | CPU pandas + XGBoost hist | `gpu` / `cpu` |
| `USE_BIGQUERY` | read forecast from BigQuery | local parquet / in-memory demo | — |
| `USE_GEMINI` | Gemini on Vertex AI | deterministic rule-based answer | `gemini` / `rules` |

With all flags off the whole product runs with **no GPU and no cloud credentials** — which
is exactly how CI exercises it.

## Acceleration

The workload that benefits from the GPU is the meter-level group-by + feature engineering
over tens of millions of rows (`pipeline/features.aggregate_zone_demand` and friends), plus
gradient-boosted tree training. `cudf.pandas` accelerates the dataframe work with no code
change; XGBoost accelerates training via `device="cuda"`. `pipeline/benchmark.py` times the
identical pipeline on CPU vs GPU and records the speedup — see [BENCHMARK.md](BENCHMARK.md).

## Technology mapping

| Layer | Used for |
| ----- | -------- |
| Cloud Storage | raw parquet data lake |
| BigQuery | forecast + risk warehouse the app reads from |
| Cloud Run | hosts the single API + SPA container (scale-to-zero) |
| Vertex AI (Gemini) | natural-language Q&A and recommendation narration |
| RAPIDS cuDF / `cudf.pandas` | GPU-accelerated dataframe pipeline |
| XGBoost (CUDA) | GPU-accelerated demand model |

## Security

No secrets in the repo (ambient credentials only); a non-root container; input bounds at
the API edge; security headers and restrictive CORS; and a least-privilege runtime service
account. See [IAM.md](../infra/IAM.md).
