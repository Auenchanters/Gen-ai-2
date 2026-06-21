"""Tests for the AI answer service (deterministic rules fallback)."""

from server import ai
from server.schemas import RiskRankRow


def _ranking():
    return [
        RiskRankRow(
            zone="Zone-2",
            risk_score=82.0,
            risk_band="critical",
            forecast_kwh=99.0,
            capacity_kwh=100.0,
            headroom_kwh=1.0,
        ),
        RiskRankRow(
            zone="Zone-1",
            risk_score=6.0,
            risk_band="low",
            forecast_kwh=55.0,
            capacity_kwh=100.0,
            headroom_kwh=45.0,
        ),
    ]


def test_rules_answer_is_grounded_in_data():
    answer, source = ai.answer_question("what is at risk?", _ranking(), use_gemini=False)
    assert source == "rules"
    assert "Zone-2" in answer
    assert "1 zone" in answer  # exactly one zone at risk


def test_rules_answer_handles_no_data():
    answer, source = ai.answer_question("anything?", [], use_gemini=False)
    assert source == "rules"
    assert "No forecast data" in answer


def test_rules_answer_when_all_zones_safe():
    ranking = [
        RiskRankRow(
            zone="Zone-1",
            risk_score=5.0,
            risk_band="low",
            forecast_kwh=50.0,
            capacity_kwh=100.0,
            headroom_kwh=50.0,
        )
    ]
    answer, source = ai.answer_question("status?", ranking, use_gemini=False)
    assert source == "rules"
    assert "within safe limits" in answer
