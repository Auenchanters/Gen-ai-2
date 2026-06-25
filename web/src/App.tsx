import { useEffect, useState } from "react";
import { getAlerts, getForecast, getHealth, getRisk } from "./api";
import { Dashboard } from "./components/Dashboard";
import { Splash } from "./components/Splash";
import type { Alert, Health, RiskRankRow, ZoneForecastPoint } from "./types";

// Single-page dashboard: tabs scroll to the relevant section rather than route.
const TABS: { label: string; target: string }[] = [
  { label: "Dashboard", target: "main" },
  { label: "Grid", target: "gauge-heading" },
  { label: "Analytics", target: "forecast-heading" },
  { label: "Incidents", target: "alerts-heading" },
];

export default function App() {
  const [health, setHealth] = useState<Health | null>(null);
  const [risk, setRisk] = useState<RiskRankRow[]>([]);
  const [forecast, setForecast] = useState<ZoneForecastPoint[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [showSplash, setShowSplash] = useState(true);
  const [activeTab, setActiveTab] = useState("Dashboard");

  function goToTab(label: string, target: string) {
    setActiveTab(label);
    const el = target === "main" ? document.getElementById("main") : document.getElementById(target);
    el?.scrollIntoView({ behavior: "smooth", block: target === "main" ? "start" : "center" });
  }

  function exportCsv() {
    if (risk.length === 0) return;
    const cols = Object.keys(risk[0]) as (keyof RiskRankRow)[];
    const rows = risk.map((r) => cols.map((c) => r[c]).join(","));
    const csv = [cols.join(","), ...rows].join("\n");
    const url = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
    const a = document.createElement("a");
    a.href = url;
    a.download = "gridpulse-risk.csv";
    a.click();
    URL.revokeObjectURL(url);
  }

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
      {showSplash && <Splash ready={!loading} onDone={() => setShowSplash(false)} />}

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
              <p className="brand-tag">Energy grid analytics</p>
            </div>
          </div>

          <nav className="nav-tabs" aria-label="Sections">
            {TABS.map((tab) => (
              <button
                key={tab.label}
                type="button"
                className={`nav-tab ${activeTab === tab.label ? "active" : ""}`}
                aria-current={activeTab === tab.label ? "true" : undefined}
                onClick={() => goToTab(tab.label, tab.target)}
              >
                {tab.label}
              </button>
            ))}
          </nav>

          <div className="nav-right">
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
            <button type="button" className="btn-ghost solid" onClick={exportCsv}>
              Export
            </button>
          </div>
        </div>
      </header>

      <main id="main" className="layout">
        <div className="page-head">
          <div>
            <p className="page-title grad-text">Citywide energy grid analytics</p>
            <p className="page-sub">
              <span className="live-dot" aria-hidden="true" /> Live · accelerated peak-risk intelligence
            </p>
          </div>
        </div>

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
