import { useState } from "react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { ZoneForecastPoint } from "../types";
import { DataTable } from "./DataTable";

type SeriesPoint = ZoneForecastPoint & { time: string };

export function ForecastChart({ points }: { points: ZoneForecastPoint[] }) {
  const zones = Array.from(new Set(points.map((p) => p.zone))).sort();
  const [zone, setZone] = useState(zones[0] ?? "");
  const series: SeriesPoint[] = points
    .filter((p) => p.zone === zone)
    .map((p) => ({ ...p, time: new Date(p.timestamp).toLocaleString() }));

  return (
    <section aria-labelledby="forecast-heading">
      <h2 id="forecast-heading">Demand forecast vs capacity</h2>
      <label htmlFor="zone-select">Zone</label>
      <select id="zone-select" value={zone} onChange={(e) => setZone(e.target.value)}>
        {zones.map((z) => (
          <option key={z} value={z}>
            {z}
          </option>
        ))}
      </select>
      <div
        role="img"
        aria-label={`Line chart of forecast demand versus capacity for ${zone}. The same data is in the table below.`}
      >
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={series} margin={{ top: 8, right: 8, bottom: 8, left: 8 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" hide />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line
              type="monotone"
              dataKey="forecast_kwh"
              name="Forecast"
              stroke="#0969da"
              dot={false}
              isAnimationActive={false}
            />
            <Line
              type="monotone"
              dataKey="capacity_kwh"
              name="Capacity"
              stroke="#b91c1c"
              dot={false}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <DataTable
        caption={`Forecast points for ${zone} (first 12)`}
        rowKey={(row) => row.timestamp}
        rows={series.slice(0, 12)}
        columns={[
          { key: "time", label: "Time" },
          { key: "forecast_kwh", label: "Forecast (kWh)" },
          { key: "capacity_kwh", label: "Capacity (kWh)" },
          { key: "risk_score", label: "Risk score" },
          { key: "risk_band", label: "Band" },
        ]}
      />
    </section>
  );
}
