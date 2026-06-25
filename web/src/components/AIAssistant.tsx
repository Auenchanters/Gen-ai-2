import type { Alert } from "../types";
import { AskBox } from "./AskBox";

/** CityOS-style "AI assistant" card: a surfaced insight from the top alert,
 *  plus the existing natural-language Ask box. */
export function AIAssistant({ alerts }: { alerts: Alert[] }) {
  const top = alerts[0];
  return (
    <section className="card col-12 reveal" aria-labelledby="assistant-heading">
      <div className="card-head">
        <h2 className="card-title" id="assistant-heading">
          AI grid assistant
        </h2>
      </div>
      {top && (
        <div className="insight">
          <span className="insight-icon" aria-hidden="true">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2Z" />
              <path d="M9 21h6" />
            </svg>
          </span>
          <div className="insight-body">
            <p className="insight-head">{top.zone} at {top.risk_band} risk</p>
            <p>{top.actions[0] ?? "Monitor and prepare load-shifting options."}</p>
          </div>
        </div>
      )}
      <AskBox />
    </section>
  );
}
