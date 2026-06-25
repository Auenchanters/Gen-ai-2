import type { RiskRankRow } from "../types";

// ponytail: demo-only decorative values — these are NOT produced by the API.
// They fill the CityOS-style status panel for the demo. Swap for real feeds later.
export interface SystemMetric {
  key: string;
  value: string;
  unit?: string;
  /** true when derived from real API data rather than a decorative placeholder. */
  real?: boolean;
}

/** Status-overview rows: a few values derived honestly from the risk feed, plus
 *  decorative grid telemetry to match the reference dashboard. */
export function systemMetrics(rows: RiskRankRow[]): SystemMetric[] {
  const totalForecast = rows.reduce((sum, r) => sum + r.forecast_kwh, 0);
  const atRisk = rows.filter(
    (r) => r.risk_band === "high" || r.risk_band === "critical",
  ).length;

  return [
    { key: "Real-time demand", value: Math.round(totalForecast).toLocaleString("en-US"), unit: "kWh", real: true },
    { key: "Zones at risk", value: String(atRisk), unit: `of ${rows.length}`, real: true },
    { key: "Avg. tariff", value: "0.38", unit: "€/kWh" },
    { key: "Active meters", value: "2.4M", unit: "units" },
    { key: "Carbon intensity", value: "142", unit: "g CO₂/kWh" },
    { key: "Grid frequency", value: "50.02", unit: "Hz" },
    { key: "Voltage stability", value: "230", unit: "V ±1.2%" },
  ];
}
