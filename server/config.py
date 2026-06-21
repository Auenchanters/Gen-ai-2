"""Application settings (feature flags + cloud config) from environment variables."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration. Every external integration is behind a default-off flag."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    use_bigquery: bool = False
    use_gemini: bool = False
    data_dir: Path = Path("data")
    forecast_file: str = "forecast.parquet"
    google_cloud_project: str = "gen-ai-2-500107"
    google_cloud_location: str = "us-central1"
    bigquery_dataset: str = "gridpulse"
    gemini_model: str = "gemini-2.5-flash"


@lru_cache
def get_settings() -> Settings:
    """Return a process-wide cached :class:`Settings` instance."""
    return Settings()
