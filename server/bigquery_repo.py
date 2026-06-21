"""BigQuery-backed forecast repository (used when ``USE_BIGQUERY=1``; lazy imports)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


class BigQueryForecastRepository:
    """Reads the forecast table from a BigQuery dataset."""

    def __init__(self, project: str, dataset: str, table: str = "forecast") -> None:
        self._project = project
        self._dataset = dataset
        self._table = table

    def get_forecast(self) -> pd.DataFrame:  # pragma: no cover - needs live BigQuery
        """Query the full forecast table into a DataFrame."""
        from google.cloud import bigquery

        client = bigquery.Client(project=self._project)
        # Identifiers come from server config, not user input.
        query = f"SELECT * FROM `{self._project}.{self._dataset}.{self._table}`"
        return client.query(query).to_dataframe()
