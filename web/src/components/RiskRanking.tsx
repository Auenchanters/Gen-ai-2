import { Bar, BarChart, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { bandColor } from "../theme";
import type { RiskRankRow } from "../types";
import { ChartTooltip } from "./ChartTooltip";
import { DataTable } from "./DataTable";
import { RiskBadge } from "./RiskBadge";

const round = (n: number) => Math.round(n).toLocaleString("en-US");

export function RiskRanking({ rows }: { rows: RiskRankRow[] }) {
  return (
    <section className="card col-8 reveal" aria-labelledby="risk-heading">
      <div className="card-head">
        <h2 className="card-title" id="risk-heading">
          Peak-risk ranking by zone
        </h2>
        <span className="card-meta">{rows.length} zones</span>
      </div>
      <div
        className="chart-wrap"
        role="img"
        aria-label="Bar chart of peak-risk score by zone. The same data is in the table below."
      >
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={rows} margin={{ top: 6, right: 6, bottom: 0, left: -18 }}>
            <XAxis dataKey="zone" tickLine={false} axisLine={false} />
            <YAxis domain={[0, 100]} width={34} tickLine={false} axisLine={false} />
            <Tooltip cursor={{ fill: "rgba(255,255,255,0.05)" }} content={<ChartTooltip />} />
            <Bar dataKey="risk_score" name="Risk score" radius={[6, 6, 0, 0]} isAnimationActive={false}>
              {rows.map((row) => (
                <Cell key={row.zone} fill={bandColor(row.risk_band)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div className="table-wrap sr-table">
        <DataTable
          caption="Zone risk ranking (highest first)"
          rowKey={(row) => row.zone}
          rows={rows}
          columns={[
            { key: "zone", label: "Zone" },
            { key: "risk_score", label: "Risk", render: (r) => <span className="num">{round(r.risk_score)}</span> },
            { key: "risk_band", label: "Band", render: (r) => <RiskBadge band={r.risk_band} /> },
            { key: "forecast_kwh", label: "Forecast", render: (r) => <span className="num">{round(r.forecast_kwh)}</span> },
            { key: "capacity_kwh", label: "Capacity", render: (r) => <span className="num">{round(r.capacity_kwh)}</span> },
            { key: "headroom_kwh", label: "Headroom", render: (r) => <span className="num">{round(r.headroom_kwh)}</span> },
          ]}
        />
      </div>
    </section>
  );
}
