import { PolarAngleAxis, RadialBar, RadialBarChart, ResponsiveContainer } from "recharts";
import type { RiskRankRow } from "../types";

/** System load = highest forecast/capacity utilization across all zones. */
function peakUtilization(rows: RiskRankRow[]): number {
  if (rows.length === 0) return 0;
  const util = rows.map((r) => (r.capacity_kwh > 0 ? (r.forecast_kwh / r.capacity_kwh) * 100 : 0));
  return Math.min(100, Math.round(Math.max(...util)));
}

export function LoadGauge({ rows }: { rows: RiskRankRow[] }) {
  const value = peakUtilization(rows);
  const stroke = value >= 90 ? "var(--critical)" : value >= 75 ? "var(--high)" : "#4da3ff";

  return (
    <section className="card gauge col-4 reveal" aria-labelledby="gauge-heading">
      <div className="card-head">
        <h2 className="card-title" id="gauge-heading">
          Total system load
        </h2>
      </div>
      <div
        className="gauge-wrap"
        role="img"
        aria-label={`Total system load is ${value} percent — the busiest zone's forecast demand against its capacity.`}
      >
        <ResponsiveContainer width="100%" height={220}>
          <RadialBarChart
            data={[{ name: "load", value }]}
            innerRadius="74%"
            outerRadius="100%"
            startAngle={230}
            endAngle={-50}
          >
            <PolarAngleAxis type="number" domain={[0, 100]} tick={false} />
            <RadialBar
              dataKey="value"
              cornerRadius={20}
              background={{ fill: "rgba(255,255,255,0.06)" }}
              fill={stroke}
              isAnimationActive={false}
            />
          </RadialBarChart>
        </ResponsiveContainer>
        <div className="gauge-center">
          <span className="gauge-value num">{value}%</span>
          <span className="gauge-label">peak zone utilization</span>
        </div>
      </div>
    </section>
  );
}
