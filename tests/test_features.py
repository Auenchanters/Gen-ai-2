"""Tests for pure feature engineering."""

import pandas as pd

from pipeline import features


def test_aggregate_zone_demand_sums_meters():
    readings = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(
                ["2024-01-01 08:00", "2024-01-01 08:00", "2024-01-01 08:30"]
            ),
            "zone": ["Zone-1", "Zone-1", "Zone-1"],
            "meter_id": [0, 1, 0],
            "kwh": [1.0, 2.0, 4.0],
        }
    )
    out = features.aggregate_zone_demand(readings)
    by_time = dict(zip(out["timestamp"], out["demand_kwh"], strict=True))
    assert by_time[pd.Timestamp("2024-01-01 08:00")] == 3.0
    assert by_time[pd.Timestamp("2024-01-01 08:30")] == 4.0


def test_calendar_features_known_values():
    df = pd.DataFrame(
        {"timestamp": pd.to_datetime(["2024-01-06 19:00"]), "zone": ["Z"], "demand_kwh": [1.0]}
    )
    out = features.add_calendar_features(df)
    assert out.loc[0, "hour"] == 19
    assert bool(out.loc[0, "is_weekend"]) is True  # 2024-01-06 is a Saturday
    assert bool(out.loc[0, "is_peak_hour"]) is True
    sin = out["tod_sin"].to_numpy()[0]
    cos = out["tod_cos"].to_numpy()[0]
    assert abs(sin * sin + cos * cos - 1.0) < 1e-9


def test_add_weather_merges_on_keys():
    demand = pd.DataFrame(
        {"timestamp": pd.to_datetime(["2024-01-01 00:00"]), "zone": ["Z"], "demand_kwh": [5.0]}
    )
    weather = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(["2024-01-01 00:00"]),
            "zone": ["Z"],
            "temp_c": [3.0],
            "humidity": [80.0],
        }
    )
    out = features.add_weather(demand, weather)
    assert out.loc[0, "temp_c"] == 3.0
    assert out.loc[0, "humidity"] == 80.0


def test_lag_features_shift_within_zone():
    df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2024-01-01", periods=4, freq="30min"),
            "zone": ["Z"] * 4,
            "demand_kwh": [10.0, 20.0, 30.0, 40.0],
        }
    )
    out = features.add_lag_features(df, lags=(1,), roll=2)
    assert list(out["lag_1"].fillna(-1.0)) == [-1.0, 10.0, 20.0, 30.0]
    # leakage-free rolling mean (window 2, shifted 1): row2 -> mean{10,20}=15, row3 -> {20,30}=25
    assert out.loc[2, "roll_mean_2"] == 15.0
    assert out.loc[3, "roll_mean_2"] == 25.0
