import { Cell, Pie, PieChart, ResponsiveContainer } from "recharts";
import { bandColor } from "../theme";
import type { RiskRankRow } from "../types";
import { DataTable } from "./DataTable";

const BANDS = ["critical", "high", "medium", "low"] as const;

export function BandDonut({ rows }: { rows: RiskRankRow[] }) {
  const data = BANDS.map((band) => ({
    band,
    count: rows.filter((r) => r.risk_band === band).length,
  })).filter((d) => d.count > 0);

  return (
    <section className="card col-4 reveal" aria-labelledby="donut-heading">
      <div className="card-head">
        <h2 className="card-title" id="donut-heading">
          Zones by risk band
        </h2>
        <span className="card-meta">{rows.length} zones</span>
      </div>
      <div
        className="gauge-wrap"
        role="img"
        aria-label="Doughnut chart of how many zones fall in each risk band. The same data is in the table below."
      >
        <ResponsiveContainer width="100%" height={170}>
          <PieChart>
            <Pie
              data={data}
              dataKey="count"
              nameKey="band"
              innerRadius="62%"
              outerRadius="100%"
              paddingAngle={2}
              isAnimationActive={false}
            >
              {data.map((d) => (
                <Cell key={d.band} fill={bandColor(d.band)} stroke="none" />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
      </div>
      <ul className="legend">
        {data.map((d) => (
          <li key={d.band}>
            <span className="dot" style={{ background: bandColor(d.band) }} aria-hidden="true" />
            <span style={{ textTransform: "capitalize" }}>{d.band}</span>
            <span className="legend-val num">{d.count}</span>
          </li>
        ))}
      </ul>
      <div className="table-wrap sr-table">
        <DataTable
          caption="Zone count by risk band"
          rowKey={(row) => row.band}
          rows={data}
          columns={[
            { key: "band", label: "Band" },
            { key: "count", label: "Zones", render: (r) => <span className="num">{r.count}</span> },
          ]}
        />
      </div>
    </section>
  );
}
