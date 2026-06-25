import { systemMetrics } from "../lib/mockMetrics";
import type { RiskRankRow } from "../types";

export function StatusOverview({ rows }: { rows: RiskRankRow[] }) {
  const metrics = systemMetrics(rows);
  return (
    <section className="card col-4 reveal" aria-labelledby="status-heading">
      <div className="card-head">
        <h2 className="card-title" id="status-heading">
          Grid status overview
        </h2>
      </div>
      <span className="status-banner">
        <span className="pill-dot" aria-hidden="true" />
        System nominal
      </span>
      <div className="kv-list">
        {metrics.map((m) => (
          <div className="kv" key={m.key}>
            <span className="kv-key">{m.key}</span>
            <span className="kv-val">
              {m.value}
              {m.unit && <span className="unit">{m.unit}</span>}
            </span>
          </div>
        ))}
      </div>
    </section>
  );
}
