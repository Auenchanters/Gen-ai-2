"""Synthetic smart-meter + weather generator.

Produces realistic half-hourly electricity demand for a set of zones, each with many
meters, plus per-zone weather. Deterministic given a seed, and scalable via
``--meters-per-zone`` and ``--days`` so the *same code* generates a small dev sample or
a 100M-row benchmark set.

Demand model = base load x daily double-peak (morning/evening) x weekday/weekend pattern
x temperature sensitivity (heating below ~15 C, cooling above ~22 C) x multiplicative
noise. Intentionally simple, but it exhibits the structure a forecaster must learn.
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

import numpy as np
import pandas as pd

HALF_HOURS_PER_DAY = 48
DEFAULT_ZONES: tuple[str, ...] = tuple(f"Zone-{i + 1}" for i in range(8))


def _daily_profile() -> np.ndarray:
    """Return a length-48 half-hourly demand multiplier with morning + evening peaks."""
    hour = np.arange(HALF_HOURS_PER_DAY) / 2.0
    morning = np.exp(-((hour - 8.0) ** 2) / (2 * 1.5**2))
    evening = np.exp(-((hour - 19.0) ** 2) / (2 * 2.0**2))
    return 0.5 + 0.6 * morning + 1.0 * evening


def _temp_factor(temp_c: np.ndarray) -> np.ndarray:
    """Return a demand multiplier from temperature (heating <15 C, cooling >22 C)."""
    heating = np.clip(15.0 - temp_c, 0.0, None) * 0.03
    cooling = np.clip(temp_c - 22.0, 0.0, None) * 0.04
    return 1.0 + heating + cooling


def generate_weather(start: str, days: int, zones: Sequence[str], seed: int) -> pd.DataFrame:
    """Generate per-(timestamp, zone) temperature and humidity."""
    rng = np.random.default_rng(seed)
    periods = days * HALF_HOURS_PER_DAY
    ts = pd.date_range(start, periods=periods, freq="30min")
    minutes = ts.hour.to_numpy() * 60 + ts.minute.to_numpy()
    seasonal = 10.0 * np.sin(2 * np.pi * (ts.dayofyear.to_numpy() - 80) / 365.0)
    daily = 5.0 * np.sin(2 * np.pi * (minutes / 60.0 - 15.0) / 24.0)
    frames = []
    for zone in zones:
        temp = 15.0 + seasonal + daily + rng.normal(0, 1.5) + rng.normal(0, 1.0, periods)
        humidity = np.clip(70.0 - 0.8 * (temp - 15.0) + rng.normal(0, 5, periods), 20, 100)
        frames.append(
            pd.DataFrame(
                {
                    "timestamp": ts,
                    "zone": zone,
                    "temp_c": temp.astype("float32"),
                    "humidity": humidity.astype("float32"),
                }
            )
        )
    return pd.concat(frames, ignore_index=True)


def generate_readings(
    start: str,
    days: int,
    zones: Sequence[str],
    meters_per_zone: int,
    weather: pd.DataFrame,
    seed: int,
) -> pd.DataFrame:
    """Generate per-(timestamp, zone, meter) half-hourly kWh consumption.

    ponytail: builds one zone fully in memory at a time; for >~50M rows write per-zone
    parquet parts (loop and append) to bound RAM instead of concatenating.
    """
    rng = np.random.default_rng(seed + 1)
    periods = days * HALF_HOURS_PER_DAY
    ts = pd.date_range(start, periods=periods, freq="30min")
    hh = np.arange(periods) % HALF_HOURS_PER_DAY
    is_weekend = ts.dayofweek.to_numpy() >= 5
    profile = _daily_profile()[hh] * np.where(is_weekend, 0.85, 1.0)
    frames = []
    for zone in zones:
        wz = weather.loc[weather["zone"] == zone].sort_values("timestamp")
        zone_shape = (profile * _temp_factor(wz["temp_c"].to_numpy())).astype("float32")
        base = rng.gamma(2.0, 0.15, size=meters_per_zone).astype("float32")
        noise = rng.lognormal(0.0, 0.3, size=(meters_per_zone, periods)).astype("float32")
        kwh = (base[:, None] * zone_shape[None, :] * noise).reshape(-1)
        frames.append(
            pd.DataFrame(
                {
                    "timestamp": np.tile(ts.to_numpy(), meters_per_zone),
                    "zone": zone,
                    "meter_id": np.repeat(np.arange(meters_per_zone, dtype="int32"), periods),
                    "kwh": kwh,
                }
            )
        )
    return pd.concat(frames, ignore_index=True)


def generate(
    start: str = "2024-01-01",
    days: int = 7,
    zones: Sequence[str] = DEFAULT_ZONES,
    meters_per_zone: int = 200,
    seed: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Generate ``(readings, weather)`` DataFrames at the given scale. Deterministic."""
    weather = generate_weather(start, days, zones, seed)
    readings = generate_readings(start, days, zones, meters_per_zone, weather, seed)
    return readings, weather


def main() -> None:
    """CLI: write ``readings.parquet`` and ``weather.parquet`` to ``--out``."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("data"))
    parser.add_argument("--zones", type=int, default=8)
    parser.add_argument("--meters-per-zone", type=int, default=200)
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--start", default="2024-01-01")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    zones = tuple(f"Zone-{i + 1}" for i in range(args.zones))
    readings, weather = generate(args.start, args.days, zones, args.meters_per_zone, args.seed)
    args.out.mkdir(parents=True, exist_ok=True)
    readings.to_parquet(args.out / "readings.parquet", index=False)
    weather.to_parquet(args.out / "weather.parquet", index=False)
    print(f"Wrote {len(readings):,} readings and {len(weather):,} weather rows to {args.out}/")


if __name__ == "__main__":  # pragma: no cover
    main()
