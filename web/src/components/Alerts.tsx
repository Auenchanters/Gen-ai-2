import type { Alert } from "../types";

export function Alerts({ alerts }: { alerts: Alert[] }) {
  return (
    <section aria-labelledby="alerts-heading">
      <h2 id="alerts-heading">Active alerts</h2>
      {alerts.length === 0 ? (
        <p>No zones are currently at high or critical risk.</p>
      ) : (
        <ul>
          {alerts.map((alert) => (
            <li key={alert.zone}>
              <strong>{alert.zone}</strong> — {alert.risk_band} (score {alert.risk_score})
              <ul>
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
