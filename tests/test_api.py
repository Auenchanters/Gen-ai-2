"""Integration tests for the FastAPI app using a fake repository (no cloud creds)."""

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from server.config import Settings, get_settings
from server.main import app, repository_dep


class _FakeRepo:
    def __init__(self, df):
        self._df = df

    def get_forecast(self):
        return self._df


def _forecast_df():
    return pd.DataFrame(
        {
            "timestamp": pd.to_datetime(["2024-01-01 18:30", "2024-01-01 18:30"]),
            "zone": ["Zone-1", "Zone-2"],
            "forecast_kwh": [50.0, 99.0],
            "capacity_kwh": [100.0, 100.0],
            "risk_score": [5.0, 82.0],
            "risk_band": ["low", "critical"],
        }
    )


@pytest.fixture
def client():
    app.dependency_overrides[repository_dep] = lambda: _FakeRepo(_forecast_df())
    app.dependency_overrides[get_settings] = lambda: Settings(use_bigquery=False, use_gemini=False)
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_health_reports_flags(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["engine"] == {"bigquery": False, "gemini": False}


def test_security_headers_present(client):
    headers = client.get("/api/health").headers
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert "Content-Security-Policy" in headers


def test_risk_ranking_orders_by_risk(client):
    data = client.get("/api/risk").json()
    assert data[0]["zone"] == "Zone-2"  # highest risk first


def test_alerts_returns_only_at_risk(client):
    data = client.get("/api/alerts").json()
    assert len(data) == 1
    assert data[0]["zone"] == "Zone-2"


def test_forecast_filter_by_zone(client):
    data = client.get("/api/forecast", params={"zone": "Zone-1"}).json()
    assert len(data) == 1
    assert data[0]["zone"] == "Zone-1"


def test_ask_uses_rules_fallback(client):
    response = client.post("/api/ask", json={"question": "what is at risk?"})
    assert response.status_code == 200
    body = response.json()
    assert body["source"] == "rules"
    assert "Zone-2" in body["answer"]


def test_ask_rejects_too_short_question(client):
    assert client.post("/api/ask", json={"question": "x"}).status_code == 422


def test_forecast_without_zone_returns_all(client):
    data = client.get("/api/forecast").json()
    assert {row["zone"] for row in data} == {"Zone-1", "Zone-2"}


def test_root_index(client):
    body = client.get("/").json()
    assert body["health"] == "/api/health"


def test_repository_dep_builds_local_repo():
    from server.config import Settings
    from server.main import repository_dep
    from server.repository import LocalForecastRepository

    assert isinstance(repository_dep(Settings(use_bigquery=False)), LocalForecastRepository)
