"""Pure feature engineering for zone-level demand forecasting.

All functions are pure: same input DataFrame -> same output, no I/O, no global state.
They use only generic pandas operations, so they run identically on CPU pandas and on
GPU-accelerated cudf.pandas.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

PEAK_HOURS = (17, 18, 19, 20)  # evening peak window (5-9pm)
MINUTES_PER_DAY = 1440


def aggregate_zone_demand(readings: pd.DataFrame) -> pd.DataFrame:
    """Sum meter-level kWh to total demand per ``(timestamp, zone)``.

    This groupby over millions of meter readings is the workload GPU acceleration
    targets, so it is deliberately kept as the pipeline's first heavy step.
    """
    return (
        readings.groupby(["timestamp", "zone"], observed=True)["kwh"]
        .sum()
        .reset_index()
        .rename(columns={"kwh": "demand_kwh"})
    )


def add_calendar_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add hour/day-of-week/weekend/month/peak flags and cyclic time-of-day encodings."""
    ts = pd.to_datetime(df["timestamp"])
    out = df.copy()
    out["hour"] = ts.dt.hour
    out["dayofweek"] = ts.dt.dayofweek
    out["is_weekend"] = ts.dt.dayofweek >= 5
    out["month"] = ts.dt.month
    out["is_peak_hour"] = ts.dt.hour.isin(PEAK_HOURS)
    minutes = ts.dt.hour * 60 + ts.dt.minute
    out["tod_sin"] = np.sin(2 * np.pi * minutes / MINUTES_PER_DAY)
    out["tod_cos"] = np.cos(2 * np.pi * minutes / MINUTES_PER_DAY)
    return out


def add_weather(demand: pd.DataFrame, weather: pd.DataFrame) -> pd.DataFrame:
    """Left-join per-zone weather onto zone demand by ``(timestamp, zone)``."""
    return demand.merge(weather, on=["timestamp", "zone"], how="left")


def add_lag_features(
    demand: pd.DataFrame, lags: tuple[int, ...] = (1, 48), roll: int = 48
) -> pd.DataFrame:
    """Add per-zone autoregressive lag features and a leakage-free rolling mean.

    The rolling mean is shifted by one step so a row never sees its own value.
    """
    out = demand.sort_values(["zone", "timestamp"]).reset_index(drop=True)
    grouped = out.groupby("zone", observed=True)["demand_kwh"]
    for lag in lags:
        out[f"lag_{lag}"] = grouped.shift(lag)
    out[f"roll_mean_{roll}"] = grouped.transform(
        lambda s: s.shift(1).rolling(roll, min_periods=1).mean()
    )
    return out
