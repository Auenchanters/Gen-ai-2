"""Tests for pure risk scoring and recommendations."""

import pytest

from pipeline import risk


def test_score_is_monotonic_and_bounded():
    low = risk.peak_risk_score(10, 100)
    mid = risk.peak_risk_score(85, 100)  # utilization == midpoint -> ~50
    high = risk.peak_risk_score(100, 100)
    assert low < mid < high
    assert 0.0 <= low < 5.0
    assert 45.0 < mid < 55.0
    assert high > 80.0


def test_utilization_validates_capacity():
    with pytest.raises(ValueError, match="capacity_kwh must be positive"):
        risk.utilization(10, 0)


def test_bands_cover_the_range():
    assert risk.risk_band(10) == "low"
    assert risk.risk_band(40) == "medium"
    assert risk.risk_band(60) == "high"
    assert risk.risk_band(90) == "critical"


def test_recommendations_escalate_with_risk():
    crit = risk.recommend_actions("Zone-1", 100, 100)
    low = risk.recommend_actions("Zone-2", 10, 100)
    assert crit.band == "critical"
    assert any("crew" in a.lower() for a in crit.actions)
    assert any("procure" in a.lower() for a in crit.actions)
    assert low.band == "low"
    assert low.headroom_kwh == 90.0
    assert len(low.actions) == 1


def test_recommendations_cover_medium_and_high_bands():
    med = risk.recommend_actions("Z", 80, 100)  # utilization 0.80 -> medium
    high = risk.recommend_actions("Z", 88, 100)  # utilization 0.88 -> high
    assert med.band == "medium"
    assert any("standby" in a.lower() for a in med.actions)
    assert high.band == "high"
    assert any("procure" in a.lower() for a in high.actions)
