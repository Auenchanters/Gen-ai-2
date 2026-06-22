import { useReveal } from "../hooks/motion";
import { computeKpis } from "../lib/kpis";
import type { Alert, RiskRankRow, ZoneForecastPoint } from "../types";
import { Alerts } from "./Alerts";
import { AskBox } from "./AskBox";
import { ForecastChart } from "./ForecastChart";
import { RiskRanking } from "./RiskRanking";
import { StatCards } from "./StatCards";

interface DashboardProps {
  risk: RiskRankRow[];
  forecast: ZoneForecastPoint[];
  alerts: Alert[];
}

export function Dashboard({ risk, forecast, alerts }: DashboardProps) {
  const ref = useReveal<HTMLDivElement>();
  return (
    <div ref={ref} className="dash">
      <StatCards kpis={computeKpis(risk)} />
      <div className="grid">
        <RiskRanking rows={risk} />
        <Alerts alerts={alerts} />
        <ForecastChart points={forecast} />
        <AskBox />
      </div>
    </div>
  );
}
