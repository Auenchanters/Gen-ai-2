import type { Alert } from "../types";
import { RiskBadge } from "./RiskBadge";

export function Alerts({ alerts }: { alerts: Alert[] }) {
  return (
    <section className="card col-4 reveal" aria-labelledby="alerts-heading">
      <div className="card-head">
        <h2 className="card-title" id="alerts-heading">
          Active alerts
        </h2>
        <span className="card-meta">{alerts.length}</span>
      </div>
      {alerts.length === 0 ? (
        <p className="empty">
          <span aria-hidden="true">✓</span> No zones at high or critical risk.
        </p>
      ) : (
        <ul className="alerts-list">
          {alerts.map((alert) => (
            <li key={alert.zone} className={`alert-item band-${alert.risk_band}`}>
              <div className="alert-top">
                <span className="alert-zone">{alert.zone}</span>
                <RiskBadge band={alert.risk_band} />
              </div>
              <ul className="alert-actions">
                {alert.actions.map((action) => (
                  <li key={action}>{action}</li>
                ))}
              </ul>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
