"""Pure peak-overload risk scoring and action recommendations.

Given a forecast demand and a zone's capacity, score the risk that demand overloads the
zone (0-100), classify it into a band, and produce rule-based action recommendations.
All pure functions, no I/O, so they are trivially testable and deterministic. The
rule-based recommendations also serve as the offline fallback when the Gemini narration
service is disabled or unavailable.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

# Utilities plan for a reserve margin: demand above ~85% of capacity erodes the safety
# buffer, so risk should climb steeply there. These encode that domain knowledge
# (NERC-style planning reserve margins are typically 10-15%).
RISK_MIDPOINT_UTILIZATION = 0.85  # utilization at which the risk score is 50
RISK_STEEPNESS = 12.0  # logistic slope
RESERVE_TARGET = 0.85  # procure back down to this utilization when at risk

# (upper-exclusive score, band) — anything at/above the last threshold is "critical".
BAND_THRESHOLDS: tuple[tuple[float, str], ...] = ((25.0, "low"), (50.0, "medium"), (75.0, "high"))


def utilization(forecast_kwh: float, capacity_kwh: float) -> float:
    """Return forecast demand as a fraction of capacity. Raises if capacity <= 0."""
    if capacity_kwh <= 0:
        raise ValueError("capacity_kwh must be positive")
    return forecast_kwh / capacity_kwh


def peak_risk_score(forecast_kwh: float, capacity_kwh: float) -> float:
    """Return a 0-100 logistic risk score from utilization (forecast / capacity)."""
    util = utilization(forecast_kwh, capacity_kwh)
    score = 100.0 / (1.0 + math.exp(-RISK_STEEPNESS * (util - RISK_MIDPOINT_UTILIZATION)))
    return round(score, 1)


def risk_band(score: float) -> str:
    """Classify a 0-100 score into low / medium / high / critical."""
    for threshold, band in BAND_THRESHOLDS:
        if score < threshold:
            return band
    return "critical"


@dataclass(frozen=True)
class Recommendation:
    """A zone's risk band, spare headroom, and ordered list of recommended actions."""

    zone: str
    score: float
    band: str
    headroom_kwh: float
    actions: tuple[str, ...]


def recommend_actions(zone: str, forecast_kwh: float, capacity_kwh: float) -> Recommendation:
    """Return rule-based recommended actions for a zone given forecast vs capacity."""
    score = peak_risk_score(forecast_kwh, capacity_kwh)
    band = risk_band(score)
    headroom = round(capacity_kwh - forecast_kwh, 1)
    actions: list[str] = []
    if band in ("high", "critical"):
        reserve_kwh = max(0, math.ceil(forecast_kwh - RESERVE_TARGET * capacity_kwh))
        actions.append(f"Procure ~{reserve_kwh} kWh additional reserve")
        actions.append("Issue demand-response / load-shift request to large consumers")
    if band == "critical":
        actions.append("Pre-position field crews for outage response")
        actions.append("Notify operations duty manager immediately")
    if band == "medium":
        actions.append("Monitor closely; place demand-response on standby")
    if band == "low":
        actions.append("No action required; nominal headroom")
    return Recommendation(
        zone=zone, score=score, band=band, headroom_kwh=headroom, actions=tuple(actions)
    )
