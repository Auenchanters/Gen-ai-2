"""Tests for the pure API domain transforms (ranking, alerts)."""

import pandas as pd

from server import domain


def _forecast():
    return pd.DataFrame(
        {
            "timestamp": pd.to_datetime(
                ["2024-01-01 18:00", "2024-01-01 18:30", "2024-01-01 18:00", "2024-01-01 18:30"]
            ),
            "zone": ["Zone-1", "Zone-1", "Zone-2", "Zone-2"],
            "forecast_kwh": [50.0, 55.0, 98.0, 99.0],
            "capacity_kwh": [100.0, 100.0, 100.0, 100.0],
            "risk_score": [5.0, 6.0, 80.0, 82.0],
            "risk_band": ["low", "low", "critical", "critical"],
        }
    )


def test_latest_risk_ranking_uses_latest_and_sorts_desc():
    ranking = domain.latest_risk_ranking(_forecast())
    assert [r.zone for r in ranking] == ["Zone-2", "Zone-1"]
    assert ranking[0].risk_score == 82.0  # latest (18:30) point, not 18:00
    assert ranking[1].headroom_kwh == 45.0  # 100 - 55


def test_latest_risk_ranking_empty_frame():
    assert domain.latest_risk_ranking(pd.DataFrame()) == []


def test_alerts_only_high_and_critical():
    alerts = domain.alerts(_forecast())
    assert len(alerts) == 1
    assert alerts[0].zone == "Zone-2"
    assert alerts[0].actions  # rule-based actions attached
