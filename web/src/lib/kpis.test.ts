import { describe, expect, it } from "vitest";
import type { RiskRankRow } from "../types";
import { computeKpis } from "./kpis";

const row = (zone: string, score: number, band: string, headroom: number): RiskRankRow => ({
  zone,
  risk_score: score,
  risk_band: band,
  forecast_kwh: 10,
  capacity_kwh: 100,
  headroom_kwh: headroom,
});

describe("computeKpis", () => {
  it("returns four zeroed tiles for no data", () => {
    const kpis = computeKpis([]);
    expect(kpis).toHaveLength(4);
    expect(kpis.every((k) => k.value === 0)).toBe(true);
  });

  it("summarizes the risk ranking", () => {
    const kpis = computeKpis([
      row("Z1", 5, "low", 80),
      row("Z2", 90, "critical", 5),
      row("Z3", 60, "high", 40),
    ]);
    const byLabel = Object.fromEntries(kpis.map((k) => [k.label, k]));
    expect(byLabel["Zones monitored"].value).toBe(3);
    expect(byLabel["Zones at risk"].value).toBe(2);
    expect(byLabel["Peak risk score"].value).toBe(90);
    expect(byLabel["Peak risk score"].sub).toBe("Z2");
    expect(byLabel["Min headroom"].value).toBe(5);
  });
});
