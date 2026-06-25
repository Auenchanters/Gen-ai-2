import { useReveal } from "../hooks/motion";
import { computeKpis } from "../lib/kpis";
import type { Alert, RiskRankRow, ZoneForecastPoint } from "../types";
import { AIAssistant } from "./AIAssistant";
import { Alerts } from "./Alerts";
import { BandDonut } from "./BandDonut";
import { ForecastBars } from "./ForecastBars";
import { ForecastChart } from "./ForecastChart";
import { LoadGauge } from "./LoadGauge";
import { RiskRanking } from "./RiskRanking";
import { StatCards } from "./StatCards";
import { StatusOverview } from "./StatusOverview";

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
        <LoadGauge rows={risk} />
        <StatusOverview rows={risk} />
        <BandDonut rows={risk} />

        <ForecastChart points={forecast} />
        <ForecastBars points={forecast} />

        <RiskRanking rows={risk} />
        <Alerts alerts={alerts} />

        <AIAssistant alerts={alerts} />
      </div>
    </div>
  );
}
