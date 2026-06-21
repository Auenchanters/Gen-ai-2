"""Pydantic request/response models for the GridPulse API (the typed contract)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ZoneForecastPoint(BaseModel):
    """A single half-hourly forecast point for one zone, with its risk."""

    timestamp: datetime
    zone: str
    forecast_kwh: float
    capacity_kwh: float
    risk_score: float
    risk_band: str


class RiskRankRow(BaseModel):
    """A zone's current standing in the risk ranking."""

    zone: str
    risk_score: float
    risk_band: str
    forecast_kwh: float
    capacity_kwh: float
    headroom_kwh: float


class Alert(BaseModel):
    """An actionable alert for a zone at high or critical risk."""

    zone: str
    risk_score: float
    risk_band: str
    actions: list[str]


class AskRequest(BaseModel):
    """A natural-language question about current grid risk."""

    question: str = Field(min_length=3, max_length=500)


class AskResponse(BaseModel):
    """An answer plus its source (``"gemini"`` or ``"rules"``)."""

    answer: str
    source: str


class Health(BaseModel):
    """Service health and which external integrations are enabled."""

    status: str
    version: str
    engine: dict[str, bool]
