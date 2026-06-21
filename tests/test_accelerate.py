"""Tests for the batch pipeline orchestration (CPU path)."""

from pipeline import accelerate
from pipeline.generate_data import generate


def test_run_pipeline_produces_clean_features():
    readings, weather = generate(days=3, zones=("Zone-1", "Zone-2"), meters_per_zone=5, seed=2)
    out = accelerate.run_pipeline(readings, weather)
    assert {"timestamp", "zone", "demand_kwh", "lag_48", "temp_c"}.issubset(out.columns)
    assert len(out) > 0
    assert out["lag_48"].notna().all()  # warm-up NaNs are dropped
    assert accelerate.ENGINE == "cpu"  # no GPU in CI


def test_load_or_generate_reads_existing_parquet(tmp_path):
    readings, weather = generate(days=1, zones=("Zone-1",), meters_per_zone=3, seed=1)
    readings.to_parquet(tmp_path / "readings.parquet", index=False)
    weather.to_parquet(tmp_path / "weather.parquet", index=False)
    loaded_readings, loaded_weather = accelerate.load_or_generate(tmp_path)
    assert len(loaded_readings) == len(readings)
    assert len(loaded_weather) == len(weather)


def test_load_or_generate_falls_back_to_generator(tmp_path):
    readings, weather = accelerate.load_or_generate(tmp_path)  # empty dir -> generate()
    assert len(readings) > 0
    assert len(weather) > 0
