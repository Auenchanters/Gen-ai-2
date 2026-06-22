import type { RiskBand } from "./types";

// AA-contrast colors on the dark theme; meaning is never encoded by color alone (a risk
// band label always accompanies these). Mirrors the --low/--medium/--high/--critical
// CSS variables in index.css.
const BAND_COLORS: Record<RiskBand, string> = {
  low: "#3fb950",
  medium: "#d6a01e",
  high: "#fb8f44",
  critical: "#f85149",
};

export function bandColor(band: string): string {
  return BAND_COLORS[band as RiskBand] ?? "#57606a";
}
