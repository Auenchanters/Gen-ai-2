"""Forecast data access: a Protocol plus a zero-setup local implementation.

Routes depend on the :class:`ForecastRepository` *interface*, never a concrete backend,
so tests can inject a fake and production can swap BigQuery for local parquet via a flag.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    import pandas as pd

    from server.config import Settings


class ForecastRepository(Protocol):
    """Interface for reading the serving forecast + risk table."""

    def get_forecast(self) -> pd.DataFrame:
        """Return the forecast table (timestamp, zone, forecast_kwh, capacity_kwh, risk_*)."""
        ...


class LocalForecastRepository:
    """Reads ``forecast.parquet``; if absent, generates a small demo so the API always works."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._cache: pd.DataFrame | None = None

    def get_forecast(self) -> pd.DataFrame:
        """Return the forecast table, caching it after the first load."""
        if self._cache is None:
            self._cache = self._load()
        return self._cache

    def _load(self) -> pd.DataFrame:
        import pandas as pd

        if self._path.exists():
            return pd.read_parquet(self._path)
        return _generate_demo_forecast()


def _generate_demo_forecast() -> pd.DataFrame:
    """Run a small end-to-end pipeline so the API has real data with zero setup."""
    from pipeline import train
    from pipeline.accelerate import run_pipeline
    from pipeline.generate_data import generate

    readings, weather = generate(days=7, meters_per_zone=30)
    features = run_pipeline(readings, weather)
    train_df, test_df = train.time_train_test_split(features)
    model = train.train_model(train_df, n_estimators=60)
    capacities = train.zone_capacities(train_df)
    horizon = test_df.groupby("zone", observed=True).tail(train.FORECAST_HORIZON_STEPS)
    return train.build_forecast_table(horizon, train.forecast(model, horizon), capacities)


def get_repository(settings: Settings) -> ForecastRepository:
    """Select the forecast repository implementation based on settings flags."""
    if settings.use_bigquery:  # pragma: no cover - needs live BigQuery
        from server.bigquery_repo import BigQueryForecastRepository

        return BigQueryForecastRepository(settings.google_cloud_project, settings.bigquery_dataset)
    return LocalForecastRepository(settings.data_dir / settings.forecast_file)
