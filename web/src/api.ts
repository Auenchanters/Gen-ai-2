import type { Alert, AskResponse, Health, RiskRankRow, ZoneForecastPoint } from "./types";

async function getJSON<T>(url: string): Promise<T> {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Request to ${url} failed: ${response.status}`);
  }
  return (await response.json()) as T;
}

export const getHealth = (): Promise<Health> => getJSON<Health>("/api/health");

export const getRisk = (): Promise<RiskRankRow[]> => getJSON<RiskRankRow[]>("/api/risk");

export const getAlerts = (): Promise<Alert[]> => getJSON<Alert[]>("/api/alerts");

export const getForecast = (zone?: string): Promise<ZoneForecastPoint[]> =>
  getJSON<ZoneForecastPoint[]>(
    zone ? `/api/forecast?zone=${encodeURIComponent(zone)}` : "/api/forecast",
  );

export async function ask(question: string): Promise<AskResponse> {
  const response = await fetch("/api/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  if (!response.ok) {
    throw new Error(`Ask failed: ${response.status}`);
  }
  return (await response.json()) as AskResponse;
}
