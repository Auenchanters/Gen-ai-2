"""CPU-vs-GPU benchmark for the dataframe pipeline (the acceleration evidence).

Times the heavy pipeline steps (zone aggregation + feature engineering) at a given data
scale. Run once per engine; on a GPU box ``--compare`` runs both in subprocesses and
prints the speedup. Results accumulate in ``benchmarks/results.json`` for the README table.

    uv run python -m pipeline.benchmark --meters-per-zone 500 --days 14   # CPU baseline
    USE_GPU=1 python -m pipeline.benchmark --meters-per-zone 500 --days 14  # GPU run
    python -m pipeline.benchmark --compare --meters-per-zone 2000 --days 30 # both + speedup
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from pipeline.engine import maybe_enable_cudf_pandas

_GPU_ENABLED = maybe_enable_cudf_pandas()
ENGINE = "gpu" if _GPU_ENABLED else "cpu"
DEFAULT_RESULTS = Path("benchmarks/results.json")


@dataclass(frozen=True)
class BenchRecord:
    """One timed run of the pipeline at a fixed scale on a single engine."""

    engine: str
    rows: int
    zones: int
    pipeline_seconds: float
    rows_per_sec: int


def run_once(meters_per_zone: int = 500, days: int = 14, zones: int = 8) -> BenchRecord:
    """Generate data at the requested scale and time the heavy pipeline steps."""
    from pipeline import features
    from pipeline.generate_data import generate

    zone_names = tuple(f"Zone-{i + 1}" for i in range(zones))
    readings, weather = generate(days=days, zones=zone_names, meters_per_zone=meters_per_zone)
    n_rows = len(readings)

    start = time.perf_counter()
    demand = features.aggregate_zone_demand(readings)
    demand = features.add_calendar_features(demand)
    demand = features.add_weather(demand, weather)
    demand = features.add_lag_features(demand)
    demand.dropna()
    elapsed = time.perf_counter() - start

    return BenchRecord(
        engine=ENGINE,
        rows=int(n_rows),
        zones=zones,
        pipeline_seconds=round(elapsed, 3),
        rows_per_sec=int(n_rows / elapsed),
    )


def save_result(record: BenchRecord, out: Path = DEFAULT_RESULTS) -> None:
    """Append a record to the results file, replacing any prior run at the same engine+scale."""
    out.parent.mkdir(parents=True, exist_ok=True)
    existing = json.loads(out.read_text()) if out.exists() else []
    kept = [r for r in existing if not (r["engine"] == record.engine and r["rows"] == record.rows)]
    kept.append(asdict(record))
    out.write_text(json.dumps(kept, indent=2))


def summarize(records: list[dict[str, Any]]) -> list[dict[str, float]]:
    """Pair CPU and GPU runs by row count and compute the speedup for each scale."""
    by_rows: dict[int, dict[str, float]] = {}
    for r in records:
        by_rows.setdefault(int(r["rows"]), {})[str(r["engine"])] = float(r["pipeline_seconds"])
    summary: list[dict[str, float]] = []
    for rows, engines in sorted(by_rows.items()):
        if "cpu" in engines and "gpu" in engines and engines["gpu"] > 0:
            summary.append(
                {
                    "rows": rows,
                    "cpu_s": engines["cpu"],
                    "gpu_s": engines["gpu"],
                    "speedup": round(engines["cpu"] / engines["gpu"], 1),
                }
            )
    return summary


def main() -> None:  # pragma: no cover
    """CLI entry point; see module docstring for usage."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--meters-per-zone", type=int, default=500)
    parser.add_argument("--days", type=int, default=14)
    parser.add_argument("--zones", type=int, default=8)
    parser.add_argument("--out", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument(
        "--compare", action="store_true", help="run CPU and GPU in subprocesses and report speedup"
    )
    args = parser.parse_args()

    if args.compare:
        for label, flag in (("cpu", "0"), ("gpu", "1")):
            print(f"running {label} ...")
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pipeline.benchmark",
                    "--meters-per-zone",
                    str(args.meters_per_zone),
                    "--days",
                    str(args.days),
                    "--zones",
                    str(args.zones),
                    "--out",
                    str(args.out),
                ],
                env={**os.environ, "USE_GPU": flag},
                check=True,
            )
        for row in summarize(json.loads(args.out.read_text())):
            print(
                f"{row['rows']:>12,.0f} rows | CPU {row['cpu_s']:>7.2f}s | "
                f"GPU {row['gpu_s']:>7.2f}s | {row['speedup']}x"
            )
        return

    record = run_once(args.meters_per_zone, args.days, args.zones)
    save_result(record, args.out)
    print(
        f"[{record.engine}] {record.rows:,} rows in {record.pipeline_seconds}s "
        f"({record.rows_per_sec:,} rows/s)"
    )


if __name__ == "__main__":  # pragma: no cover
    main()
