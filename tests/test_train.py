"""Tests for the forecasting model and serving-table assembly (CPU path)."""

from pipeline import accelerate, train
from pipeline.generate_data import generate


def _feature_frame():
    readings, weather = generate(days=7, zones=("Zone-1", "Zone-2"), meters_per_zone=10, seed=5)
    return accelerate.run_pipeline(readings, weather)


def test_split_is_chronological():
    df = _feature_frame()
    train_df, test_df = train.time_train_test_split(df, 0.8)
    assert len(train_df) + len(test_df) == len(df)
    assert train_df["timestamp"].max() <= test_df["timestamp"].min()


def test_train_forecast_and_evaluate():
    df = _feature_frame()
    train_df, test_df = train.time_train_test_split(df, 0.8)
    model = train.train_model(train_df, n_estimators=20)
    preds = train.forecast(model, test_df)
    assert len(preds) == len(test_df)
    metrics = train.evaluate(test_df[train.TARGET], preds)
    assert set(metrics) == {"mae", "rmse", "mape_pct"}
    assert metrics["mae"] >= 0.0


def test_zone_capacities_and_forecast_table():
    df = _feature_frame()
    train_df, test_df = train.time_train_test_split(df, 0.8)
    capacities = train.zone_capacities(train_df)
    assert set(capacities) == {"Zone-1", "Zone-2"}
    assert all(value > 0 for value in capacities.values())

    model = train.train_model(train_df, n_estimators=20)
    horizon = test_df.tail(20)
    table = train.build_forecast_table(horizon, train.forecast(model, horizon), capacities)
    expected = {"timestamp", "zone", "forecast_kwh", "capacity_kwh", "risk_score", "risk_band"}
    assert expected.issubset(table.columns)
    assert table["risk_band"].isin(["low", "medium", "high", "critical"]).all()
