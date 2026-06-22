import { useEffect, useState } from "react";
import { getAlerts, getForecast, getHealth, getRisk } from "./api";
import { Dashboard } from "./components/Dashboard";
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
      <header className="app-header">
        <div className="app-header-inner">
          <div className="brand">
            <span className="brand-logo" aria-hidden="true">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
                <path d="M13 2 4 14h7l-1 8 9-12h-7l1-8Z" />
              </svg>
            </span>
            <div>
              <h1 className="brand-name">GridPulse</h1>
              <p className="brand-tag">Accelerated energy demand &amp; peak-risk intelligence</p>
            </div>
          </div>
          <div className="status-pills">
            <span className={`pill ${health?.engine.bigquery ? "on" : ""}`}>
              <span className="pill-dot" aria-hidden="true" />
              BigQuery {health?.engine.bigquery ? "on" : "off"}
            </span>
            <span className={`pill ${health?.engine.gemini ? "on" : ""}`}>
              <span className="pill-dot" aria-hidden="true" />
              Gemini {health?.engine.gemini ? "on" : "off"}
            </span>
          </div>
        </div>
      </header>

      <main id="main" className="layout">
        {loading && (
          <div className="skeleton" role="status" aria-live="polite">
            <span className="sr-only">Loading dashboard…</span>
            <div className="sk-kpis" aria-hidden="true">
              <div className="sk-block" />
              <div className="sk-block" />
              <div className="sk-block" />
              <div className="sk-block" />
            </div>
            <div className="sk-block sk-wide" aria-hidden="true" />
            <div className="sk-block sk-wide" aria-hidden="true" />
          </div>
        )}
        {error && (
          <p className="alert-banner error" role="alert">
            {error}
          </p>
        )}
        {!loading && !error && <Dashboard risk={risk} forecast={forecast} alerts={alerts} />}
      </main>

      <footer className="footer">
        {health ? (
          <p>
            API v{health.version} · BigQuery {health.engine.bigquery ? "on" : "off"} · Gemini{" "}
            {health.engine.gemini ? "on" : "off"} · accelerated with RAPIDS + XGBoost
          </p>
        ) : (
          <p>GridPulse</p>
        )}
      </footer>
    </>
  );
}
