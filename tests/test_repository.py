"""Tests for forecast repositories (local parquet + zero-setup demo generation)."""

import pandas as pd

from server.config import Settings
from server.repository import LocalForecastRepository, get_repository


def _forecast_df():
    return pd.DataFrame(
        {
            "timestamp": pd.to_datetime(["2024-01-01 00:00"]),
            "zone": ["Zone-1"],
            "forecast_kwh": [1.0],
            "capacity_kwh": [2.0],
            "risk_score": [1.0],
            "risk_band": ["low"],
        }
    )


def test_local_repo_reads_and_caches_parquet(tmp_path):
    path = tmp_path / "forecast.parquet"
    _forecast_df().to_parquet(path, index=False)
    repo = LocalForecastRepository(path)
    first = repo.get_forecast()
    assert len(first) == 1
    assert repo.get_forecast() is first  # cached, not re-read


def test_local_repo_generates_demo_when_file_missing(tmp_path):
    repo = LocalForecastRepository(tmp_path / "missing.parquet")
    out = repo.get_forecast()
    assert len(out) > 0
    assert {"zone", "forecast_kwh", "risk_score", "risk_band"}.issubset(out.columns)


def test_get_repository_defaults_to_local():
    repo = get_repository(Settings(use_bigquery=False))
    assert isinstance(repo, LocalForecastRepository)


def test_bigquery_repo_stores_config():
    from server.bigquery_repo import BigQueryForecastRepository

    repo = BigQueryForecastRepository("proj", "ds", "tbl")
    assert (repo._project, repo._dataset, repo._table) == ("proj", "ds", "tbl")


def test_get_settings_returns_settings_instance():
    from server.config import get_settings

    assert isinstance(get_settings(), Settings)
