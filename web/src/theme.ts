import type { RiskBand } from "./types";

// WCAG-AA contrast colors on a light background; meaning is never encoded by color alone
// (the risk band label always accompanies these).
const BAND_COLORS: Record<RiskBand, string> = {
  low: "#1a7f37",
  medium: "#9a6700",
  high: "#bc4c00",
  critical: "#b91c1c",
};

export function bandColor(band: string): string {
  return BAND_COLORS[band as RiskBand] ?? "#57606a";
}
