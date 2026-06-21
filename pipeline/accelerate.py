"""Offline batch pipeline: turn raw meter readings into model-ready zone features.

Imported at process start, this module enables RAPIDS ``cudf.pandas`` when ``USE_GPU=1``
so the heavy dataframe work (zone aggregation, feature engineering) runs on the GPU. The
transforms themselves live in :mod:`pipeline.features` and are engine-agnostic, so the
*same code* runs on CPU pandas or GPU cuDF. ``pandas`` is imported lazily inside the
functions below — after the accelerator has been installed.
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path
from typing import TYPE_CHECKING

from pipeline.engine import maybe_enable_cudf_pandas

if TYPE_CHECKING:
    import pandas as pd

_GPU_ENABLED = maybe_enable_cudf_pandas()
ENGINE = "gpu" if _GPU_ENABLED else "cpu"


def run_pipeline(readings: pd.DataFrame, weather: pd.DataFrame) -> pd.DataFrame:
    """Aggregate to zone demand, add calendar + weather + lag features, drop warm-up NaNs."""
    from pipeline import features

    demand = features.aggregate_zone_demand(readings)
    demand = features.add_calendar_features(demand)
    demand = features.add_weather(demand, weather)
    demand = features.add_lag_features(demand)
    return demand.dropna().reset_index(drop=True)


def load_or_generate(data_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load readings/weather parquet from ``data_dir``, or generate a default sample."""
    import pandas as pd

    readings_path = data_dir / "readings.parquet"
    weather_path = data_dir / "weather.parquet"
    if readings_path.exists() and weather_path.exists():
        return pd.read_parquet(readings_path), pd.read_parquet(weather_path)

    from pipeline.generate_data import generate

    return generate()


def main() -> None:  # pragma: no cover
    """CLI: build the zone feature table and write it to ``--out``."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--out", type=Path, default=Path("data/zone_features.parquet"))
    args = parser.parse_args()

    readings, weather = load_or_generate(args.data_dir)
    start = time.perf_counter()
    features_df = run_pipeline(readings, weather)
    elapsed = time.perf_counter() - start

    args.out.parent.mkdir(parents=True, exist_ok=True)
    features_df.to_parquet(args.out, index=False)
    print(
        f"[{ENGINE}] processed {len(readings):,} readings -> {len(features_df):,} feature "
        f"rows in {elapsed:.2f}s; wrote {args.out}"
    )


if __name__ == "__main__":  # pragma: no cover
    main()
