import { useEffect, useState } from "react";
import { getAlerts, getForecast, getHealth, getRisk } from "./api";
import { Alerts } from "./components/Alerts";
import { AskBox } from "./components/AskBox";
import { ForecastChart } from "./components/ForecastChart";
import { RiskRanking } from "./components/RiskRanking";
import type { Alert, Health, RiskRankRow, ZoneForecastPoint } from "./types";

export default function App() {
  const [health, setHealth] = useState<Health | null>(null);
  const [risk, setRisk] = useState<RiskRankRow[]>([]);
  const [forecast, setForecast] = useState<ZoneForecastPoint[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getHealth(), getRisk(), getForecast(), getAlerts()])
      .then(([h, r, f, a]) => {
        setHealth(h);
        setRisk(r);
        setForecast(f);
        setAlerts(a);
      })
      .catch(() => setError("Could not load dashboard data. Is the API running?"))
      .finally(() => setLoading(false));
  }, []);

  return (
    <>
      <a href="#main" className="skip-link">
        Skip to content
      </a>
      <header>
        <h1>GridPulse</h1>
        <p>Accelerated energy demand &amp; peak-risk intelligence</p>
      </header>
      <main id="main">
        {loading && (
          <p role="status" aria-live="polite">
            Loading dashboard…
          </p>
        )}
        {error && (
          <p role="alert" className="error">
            {error}
          </p>
        )}
        {!loading && !error && (
          <>
            <Alerts alerts={alerts} />
            <RiskRanking rows={risk} />
            <ForecastChart points={forecast} />
            <AskBox />
          </>
        )}
      </main>
      <footer>
        {health && (
          <p>
            API v{health.version} · BigQuery {health.engine.bigquery ? "on" : "off"} · Gemini{" "}
            {health.engine.gemini ? "on" : "off"}
          </p>
        )}
      </footer>
    </>
  );
}
