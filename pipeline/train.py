"""Demand-forecasting model (XGBoost) and the serving forecast + risk table.

XGBoost runs on CPU or GPU from the *same code* via its ``device`` parameter, so training
accelerates on an NVIDIA GPU (``device="cuda"``) with no code change. Feature engineering
is done upstream in :mod:`pipeline.accelerate` / :mod:`pipeline.features`.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd

from pipeline import risk
from pipeline.engine import gpu_available

if TYPE_CHECKING:
    from numpy.typing import NDArray

FEATURE_COLUMNS = [
    "hour",
    "dayofweek",
    "is_weekend",
    "month",
    "is_peak_hour",
    "tod_sin",
    "tod_cos",
    "temp_c",
    "humidity",
    "lag_1",
    "lag_48",
    "roll_mean_48",
]
TARGET = "demand_kwh"
CAPACITY_MARGIN = 1.10  # zone capacity = 1.10 x in-sample peak demand
FORECAST_HORIZON_STEPS = 96  # 48 hours at half-hourly resolution


def time_train_test_split(
    df: pd.DataFrame, train_frac: float = 0.8
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split chronologically so the test set is strictly after the train set (no leakage)."""
    ordered = df.sort_values("timestamp").reset_index(drop=True)
    cut = int(len(ordered) * train_frac)
    return ordered.iloc[:cut].copy(), ordered.iloc[cut:].copy()


def train_model(train_df: pd.DataFrame, n_estimators: int = 300, device: str | None = None) -> Any:
    """Train an XGBoost demand model; uses GPU (``device="cuda"``) automatically if available.

    Uses XGBoost's native API (not the sklearn wrapper) to avoid a scikit-learn dependency.
    """
    import xgboost as xgb

    resolved = device or ("cuda" if gpu_available() else "cpu")
    dtrain = xgb.DMatrix(
        train_df[FEATURE_COLUMNS].astype("float32"), label=train_df[TARGET].astype("float32")
    )
    params = {
        "objective": "reg:squarederror",
        "max_depth": 6,
        "eta": 0.1,
        "subsample": 0.9,
        "tree_method": "hist",
        "device": resolved,
        "seed": 42,
    }
    return xgb.train(params, dtrain, num_boost_round=n_estimators)


def forecast(model: Any, df: pd.DataFrame) -> NDArray[np.float64]:
    """Predict demand for every row of ``df``."""
    import xgboost as xgb

    dmatrix = xgb.DMatrix(df[FEATURE_COLUMNS].astype("float32"))
    return np.asarray(model.predict(dmatrix), dtype="float64")


def evaluate(y_true: Any, y_pred: Any) -> dict[str, float]:
    """Return MAE, RMSE, and MAPE (%) for a set of predictions."""
    yt = np.asarray(y_true, dtype="float64")
    yp = np.asarray(y_pred, dtype="float64")
    err = yp - yt
    mae = float(np.mean(np.abs(err)))
    rmse = float(np.sqrt(np.mean(err**2)))
    mape = float(np.mean(np.abs(err) / np.clip(np.abs(yt), 1e-6, None)) * 100.0)
    return {"mae": round(mae, 3), "rmse": round(rmse, 3), "mape_pct": round(mape, 2)}


def zone_capacities(train_df: pd.DataFrame) -> dict[str, float]:
    """Estimate each zone's capacity as a margin above its in-sample peak demand."""
    peak = train_df.groupby("zone", observed=True)[TARGET].max()
    return {str(zone): float(value) * CAPACITY_MARGIN for zone, value in peak.items()}


def build_forecast_table(
    horizon_df: pd.DataFrame, preds: Any, capacities: dict[str, float]
) -> pd.DataFrame:
    """Assemble the serving table: per row forecast, capacity, risk score, and risk band.

    Intended for the (small) forecast horizon, so scalar risk scoring per row is fine.
    """
    out = horizon_df[["timestamp", "zone"]].reset_index(drop=True)
    out["forecast_kwh"] = np.round(preds, 2)
    out["capacity_kwh"] = [round(capacities[str(zone)], 2) for zone in out["zone"]]
    scores = [
        risk.peak_risk_score(f, c)
        for f, c in zip(out["forecast_kwh"], out["capacity_kwh"], strict=True)
    ]
    out["risk_score"] = scores
    out["risk_band"] = [risk.risk_band(s) for s in scores]
    return out


def main() -> None:  # pragma: no cover
    """CLI: train on the feature table, evaluate, and write the serving forecast table."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", type=Path, default=Path("data/zone_features.parquet"))
    parser.add_argument("--out", type=Path, default=Path("data/forecast.parquet"))
    parser.add_argument("--n-estimators", type=int, default=300)
    args = parser.parse_args()

    df = pd.read_parquet(args.features)
    train_df, test_df = time_train_test_split(df)
    model = train_model(train_df, n_estimators=args.n_estimators)
    metrics = evaluate(test_df[TARGET], forecast(model, test_df))
    print(f"backtest metrics: {metrics}")

    capacities = zone_capacities(train_df)
    horizon = test_df.groupby("zone", observed=True).tail(FORECAST_HORIZON_STEPS)
    table = build_forecast_table(horizon, forecast(model, horizon), capacities)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    table.to_parquet(args.out, index=False)
    print(f"wrote {len(table):,} forecast rows to {args.out}")


if __name__ == "__main__":  # pragma: no cover
    main()
