import { render, screen } from "@testing-library/react";
import { expect, it } from "vitest";
import type { RiskRankRow } from "../types";
import { a11yViolations } from "../testUtils";
import { RiskRanking } from "./RiskRanking";

const rows: RiskRankRow[] = [
  {
    zone: "Zone-2",
    risk_score: 82,
    risk_band: "critical",
    forecast_kwh: 99,
    capacity_kwh: 100,
    headroom_kwh: 1,
  },
  {
    zone: "Zone-1",
    risk_score: 5,
    risk_band: "low",
    forecast_kwh: 50,
    capacity_kwh: 100,
    headroom_kwh: 50,
  },
];

it("renders a heading and an accessible data-table equivalent of the chart", async () => {
  const { container } = render(<RiskRanking rows={rows} />);
  expect(screen.getByRole("heading", { name: /risk ranking/i })).toBeInTheDocument();
  expect(screen.getByRole("table", { name: /risk ranking/i })).toBeInTheDocument();
  expect(screen.getByRole("cell", { name: "Zone-2" })).toBeInTheDocument();
  expect(await a11yViolations(container)).toEqual([]);
});
