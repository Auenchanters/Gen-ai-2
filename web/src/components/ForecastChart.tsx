import { useState } from "react";
import {
  Area,
  CartesianGrid,
  ComposedChart,
  Legend,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { ZoneForecastPoint } from "../types";
import { ChartTooltip } from "./ChartTooltip";
import { DataTable } from "./DataTable";
import { RiskBadge } from "./RiskBadge";

type SeriesPoint = ZoneForecastPoint & { time: string };

const round = (n: number) => Math.round(n).toLocaleString("en-US");

export function ForecastChart({ points }: { points: ZoneForecastPoint[] }) {
  const zones = Array.from(new Set(points.map((p) => p.zone))).sort();
  const [zone, setZone] = useState(zones[0] ?? "");
  const series: SeriesPoint[] = points
    .filter((p) => p.zone === zone)
    .map((p) => ({ ...p, time: new Date(p.timestamp).toLocaleString() }));

  return (
    <section className="card col-12 reveal" aria-labelledby="forecast-heading">
      <div className="card-head">
        <h2 className="card-title" id="forecast-heading">
          Demand forecast vs capacity
        </h2>
        <span>
          <label htmlFor="zone-select">Zone</label>
          <select id="zone-select" value={zone} onChange={(event) => setZone(event.target.value)}>
            {zones.map((z) => (
              <option key={z} value={z}>
                {z}
              </option>
            ))}
          </select>
        </span>
      </div>
      <div
        className="chart-wrap"
        role="img"
        aria-label={`Line chart of forecast demand versus capacity for ${zone}. The same data is in the table below.`}
      >
        <ResponsiveContainer width="100%" height={260}>
          <ComposedChart data={series} margin={{ top: 6, right: 8, bottom: 0, left: -18 }}>
            <defs>
              <linearGradient id="fc-fill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#6d8bff" stopOpacity={0.3} />
                <stop offset="100%" stopColor="#6d8bff" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="rgba(255,255,255,0.06)" vertical={false} />
            <XAxis dataKey="time" hide />
            <YAxis width={40} tickLine={false} axisLine={false} />
            <Tooltip content={<ChartTooltip />} />
            <Legend />
            <Area
              type="monotone"
              dataKey="forecast_kwh"
              name="Forecast"
              stroke="#6d8bff"
              strokeWidth={2}
              fill="url(#fc-fill)"
              isAnimationActive={false}
            />
            <Line
              type="monotone"
              dataKey="capacity_kwh"
              name="Capacity"
              stroke="#f85149"
              strokeWidth={1.5}
              strokeDasharray="5 4"
              dot={false}
              isAnimationActive={false}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
      <div className="table-wrap">
        <DataTable
          caption={`Forecast points for ${zone} (first 12)`}
          rowKey={(row) => row.timestamp}
          rows={series.slice(0, 12)}
          columns={[
            { key: "time", label: "Time" },
            { key: "forecast_kwh", label: "Forecast", render: (r) => <span className="num">{round(r.forecast_kwh)}</span> },
            { key: "capacity_kwh", label: "Capacity", render: (r) => <span className="num">{round(r.capacity_kwh)}</span> },
            { key: "risk_score", label: "Risk", render: (r) => <span className="num">{round(r.risk_score)}</span> },
            { key: "risk_band", label: "Band", render: (r) => <RiskBadge band={r.risk_band} /> },
          ]}
        />
      </div>
    </section>
  );
}
