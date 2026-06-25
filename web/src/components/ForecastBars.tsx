import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { ZoneForecastPoint } from "../types";
import { ChartTooltip } from "./ChartTooltip";
import { DataTable } from "./DataTable";

const round = (n: number) => Math.round(n).toLocaleString("en-US");
const hh = (ts: string) => new Date(ts).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

/** Peak-load forecast bars for the busiest zone (highest risk_score). */
export function ForecastBars({ points }: { points: ZoneForecastPoint[] }) {
  const peak = points.reduce<ZoneForecastPoint | null>(
    (best, p) => (best && best.risk_score >= p.risk_score ? best : p),
    null,
  );
  const zone = peak?.zone ?? "";
  const series = points
    .filter((p) => p.zone === zone)
    .map((p) => ({ ...p, time: hh(p.timestamp) }))
    .slice(0, 24);

  return (
    <section className="card col-4 reveal" aria-labelledby="peakbars-heading">
      <div className="card-head">
        <h2 className="card-title" id="peakbars-heading">
          Peak-load forecast
        </h2>
        <span className="card-meta">{zone}</span>
      </div>
      <div
        className="chart-wrap"
        role="img"
        aria-label={`Bar chart of forecast demand over time for the busiest zone, ${zone}. The same data is in the table below.`}
      >
        <ResponsiveContainer width="100%" height={170}>
          <BarChart data={series} margin={{ top: 6, right: 6, bottom: 0, left: -20 }}>
            <CartesianGrid stroke="rgba(255,255,255,0.06)" vertical={false} />
            <XAxis dataKey="time" tickLine={false} axisLine={false} interval="preserveStartEnd" />
            <YAxis width={40} tickLine={false} axisLine={false} />
            <Tooltip cursor={{ fill: "rgba(255,255,255,0.05)" }} content={<ChartTooltip />} />
            <Bar dataKey="forecast_kwh" name="Forecast" fill="#4da3ff" radius={[4, 4, 0, 0]} isAnimationActive={false} />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div className="table-wrap sr-table">
        <DataTable
          caption={`Forecast demand for ${zone}`}
          rowKey={(row) => row.timestamp}
          rows={series}
          columns={[
            { key: "time", label: "Time" },
            { key: "forecast_kwh", label: "Forecast kWh", render: (r) => <span className="num">{round(r.forecast_kwh)}</span> },
          ]}
        />
      </div>
    </section>
  );
}
