"""Pure transforms over the forecast table for the API (risk ranking, alerts).

No I/O: takes a forecast DataFrame, returns typed models. Reuses the pure scoring rules
from :mod:`pipeline.risk` so the API and the offline pipeline agree by construction.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pipeline import risk
from server.schemas import Alert, RiskRankRow

if TYPE_CHECKING:
    import pandas as pd


def latest_risk_ranking(forecast: pd.DataFrame) -> list[RiskRankRow]:
    """Return the most recent forecast per zone, ranked by risk score (highest first)."""
    if forecast.empty:
        return []
    latest = forecast.sort_values("timestamp").groupby("zone", observed=True).tail(1)
    rows = [
        RiskRankRow(
            zone=str(rec["zone"]),
            risk_score=float(rec["risk_score"]),
            risk_band=str(rec["risk_band"]),
            forecast_kwh=float(rec["forecast_kwh"]),
            capacity_kwh=float(rec["capacity_kwh"]),
            headroom_kwh=round(float(rec["capacity_kwh"]) - float(rec["forecast_kwh"]), 1),
        )
        for rec in latest.to_dict("records")
    ]
    rows.sort(key=lambda row: row.risk_score, reverse=True)
    return rows


def alerts(forecast: pd.DataFrame) -> list[Alert]:
    """Return actionable alerts for zones currently at high or critical risk."""
    out: list[Alert] = []
    for row in latest_risk_ranking(forecast):
        if row.risk_band in ("high", "critical"):
            recommendation = risk.recommend_actions(row.zone, row.forecast_kwh, row.capacity_kwh)
            out.append(
                Alert(
                    zone=row.zone,
                    risk_score=row.risk_score,
                    risk_band=row.risk_band,
                    actions=list(recommendation.actions),
                )
            )
    return out
