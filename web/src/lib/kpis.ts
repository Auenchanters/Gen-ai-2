import type { RiskRankRow } from "../types";

export interface Kpi {
  label: string;
  value: number;
  sub: string;
}

/** Derive the headline KPI tiles from the current per-zone risk ranking. Pure. */
export function computeKpis(rows: RiskRankRow[]): Kpi[] {
  if (rows.length === 0) {
    return [
      { label: "Zones monitored", value: 0, sub: "no data yet" },
      { label: "Zones at risk", value: 0, sub: "high or critical" },
      { label: "Peak risk score", value: 0, sub: "—" },
      { label: "Min headroom", value: 0, sub: "kWh" },
    ];
  }
  const atRisk = rows.filter((r) => r.risk_band === "high" || r.risk_band === "critical");
  const peak = rows.reduce((best, r) => (r.risk_score > best.risk_score ? r : best));
  const tightest = rows.reduce((min, r) => (r.headroom_kwh < min.headroom_kwh ? r : min));
  return [
    { label: "Zones monitored", value: rows.length, sub: "live feeds" },
    { label: "Zones at risk", value: atRisk.length, sub: "high or critical" },
    { label: "Peak risk score", value: Math.round(peak.risk_score), sub: peak.zone },
    { label: "Min headroom", value: Math.round(tightest.headroom_kwh), sub: `kWh · ${tightest.zone}` },
  ];
}
