import { useCountUp } from "../hooks/motion";
import type { Kpi } from "../lib/kpis";

function Stat({ kpi, hero }: { kpi: Kpi; hero?: boolean }) {
  const value = useCountUp(kpi.value);
  return (
    <div className={`stat reveal${hero ? " stat-hero" : ""}`}>
      <p className="stat-label">{kpi.label}</p>
      <p className="stat-value num">{Math.round(value).toLocaleString("en-US")}</p>
      <p className="stat-sub">{kpi.sub}</p>
    </div>
  );
}

export function StatCards({ kpis }: { kpis: Kpi[] }) {
  return (
    <section className="kpis" aria-label="Key metrics">
      {kpis.map((kpi, i) => (
        <Stat key={kpi.label} kpi={kpi} hero={i === 0} />
      ))}
    </section>
  );
}
