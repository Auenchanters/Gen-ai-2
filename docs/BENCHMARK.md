# Acceleration benchmark (CPU vs GPU)

[pipeline/benchmark.py](../pipeline/benchmark.py) times the heavy dataframe pipeline
(zone aggregation + feature engineering) and records results to
[benchmarks/results.json](../benchmarks/results.json), which feeds the README table.

Row count = `zones x meters_per_zone x days x 48`. Scale it up to make the GPU advantage
obvious (the GPU wins bigger as data grows).

## CPU baseline (runs anywhere, no GPU)

```bash
uv run python -m pipeline.benchmark --meters-per-zone 500 --days 14
```

## GPU run (free Colab/Kaggle T4 or a short GCP L4)

On a CUDA machine with RAPIDS `cudf` installed, the pipeline accelerates with no code
change — just set the flag:

```bash
USE_GPU=1 python -m pipeline.benchmark --meters-per-zone 500 --days 14
```

Run both and print the speedup in one command:

```bash
python -m pipeline.benchmark --compare --meters-per-zone 2000 --days 30
```

### On Google Colab (GPU runtime)

Open [notebooks/benchmark_colab.ipynb](../notebooks/benchmark_colab.ipynb), or run:

```bash
!git clone https://github.com/Auenchanters/Gen-ai-2 && cd Gen-ai-2
!pip install -q --extra-index-url=https://pypi.nvidia.com cudf-cu12
!pip install -qe .
!python -m pipeline.benchmark --compare --meters-per-zone 2000 --days 30
```

Then commit the updated `benchmarks/results.json`; the README acceleration table reflects
the numbers automatically.

## How it stays honest

- The exact same transform code (`pipeline/features.py`) runs on both engines — the only
  difference is whether `cudf.pandas` is active (`USE_GPU=1`).
- Generation time is excluded; only the pipeline steps are timed.
- Each `(engine, rows)` pair is deduplicated, so re-running overwrites the prior number.
