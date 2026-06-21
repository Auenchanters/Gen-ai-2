"""Tests for the synthetic data generator: shape, determinism, and value ranges."""

import sys

import pandas as pd

from pipeline import generate_data
from pipeline.generate_data import HALF_HOURS_PER_DAY, generate


def test_generate_shape_and_determinism():
    zones = ("Zone-1", "Zone-2")
    r1, w1 = generate(days=2, zones=zones, meters_per_zone=5, seed=7)
    r2, w2 = generate(days=2, zones=zones, meters_per_zone=5, seed=7)

    periods = 2 * HALF_HOURS_PER_DAY
    assert len(r1) == len(zones) * 5 * periods
    assert len(w1) == len(zones) * periods
    assert set(r1.columns) == {"timestamp", "zone", "meter_id", "kwh"}
    assert set(w1.columns) == {"timestamp", "zone", "temp_c", "humidity"}
    pd.testing.assert_frame_equal(r1, r2)
    pd.testing.assert_frame_equal(w1, w2)


def test_readings_positive_and_weather_bounded():
    readings, weather = generate(days=1, zones=("Zone-1",), meters_per_zone=10, seed=1)
    assert (readings["kwh"] > 0).all()
    assert weather["humidity"].between(20, 100).all()
    assert weather["temp_c"].between(-30, 60).all()


def test_demand_has_evening_peak():
    # Aggregated demand at the 19:00 evening peak should exceed the 03:00 overnight low.
    readings, _ = generate(days=3, zones=("Zone-1",), meters_per_zone=50, seed=3)
    readings["hour"] = readings["timestamp"].dt.hour
    by_hour = readings.groupby("hour")["kwh"].sum()
    assert by_hour[19] > by_hour[3]


def test_main_writes_parquet(monkeypatch, tmp_path):
    argv = ["prog", "--out", str(tmp_path), "--zones", "1", "--meters-per-zone", "2", "--days", "1"]
    monkeypatch.setattr(sys, "argv", argv)
    generate_data.main()
    assert (tmp_path / "readings.parquet").exists()
    assert (tmp_path / "weather.parquet").exists()
