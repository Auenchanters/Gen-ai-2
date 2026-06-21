import { Bar, BarChart, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { bandColor } from "../theme";
import type { RiskRankRow } from "../types";
import { DataTable } from "./DataTable";

export function RiskRanking({ rows }: { rows: RiskRankRow[] }) {
  return (
    <section aria-labelledby="risk-heading">
      <h2 id="risk-heading">Zone peak-risk ranking</h2>
      <div
        role="img"
        aria-label="Bar chart of peak-risk score by zone. The same data is in the table below."
      >
        <ResponsiveContainer width="100%" height={240}>
          <BarChart data={rows} margin={{ top: 8, right: 8, bottom: 8, left: 8 }}>
            <XAxis dataKey="zone" />
            <YAxis domain={[0, 100]} />
            <Tooltip />
            <Bar dataKey="risk_score" name="Risk score" isAnimationActive={false}>
              {rows.map((row) => (
                <Cell key={row.zone} fill={bandColor(row.risk_band)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      <DataTable
        caption="Zone risk ranking (highest first)"
        rowKey={(row) => row.zone}
        rows={rows}
        columns={[
          { key: "zone", label: "Zone" },
          { key: "risk_score", label: "Risk score" },
          { key: "risk_band", label: "Band" },
          { key: "forecast_kwh", label: "Forecast (kWh)" },
          { key: "capacity_kwh", label: "Capacity (kWh)" },
          { key: "headroom_kwh", label: "Headroom (kWh)" },
        ]}
      />
    </section>
  );
}
