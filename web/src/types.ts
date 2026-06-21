// These interfaces mirror the backend Pydantic schemas in server/schemas.py.

export type RiskBand = "low" | "medium" | "high" | "critical";

export interface ZoneForecastPoint {
  timestamp: string;
  zone: string;
  forecast_kwh: number;
  capacity_kwh: number;
  risk_score: number;
  risk_band: string;
}

export interface RiskRankRow {
  zone: string;
  risk_score: number;
  risk_band: string;
  forecast_kwh: number;
  capacity_kwh: number;
  headroom_kwh: number;
}

export interface Alert {
  zone: string;
  risk_score: number;
  risk_band: string;
  actions: string[];
}

export interface AskResponse {
  answer: string;
  source: string;
}

export interface Health {
  status: string;
  version: string;
  engine: Record<string, boolean>;
}
