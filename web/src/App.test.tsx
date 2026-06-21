import { render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import App from "./App";
import { a11yViolations } from "./testUtils";

function jsonResponse(body: unknown) {
  return new Response(JSON.stringify(body), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });
}

beforeEach(() => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/api/health")) {
        return jsonResponse({
          status: "ok",
          version: "0.1.0",
          engine: { bigquery: false, gemini: false },
        });
      }
      if (url.includes("/api/risk")) {
        return jsonResponse([
          {
            zone: "Zone-2",
            risk_score: 82,
            risk_band: "critical",
            forecast_kwh: 99,
            capacity_kwh: 100,
            headroom_kwh: 1,
          },
        ]);
      }
      if (url.includes("/api/alerts")) {
        return jsonResponse([
          { zone: "Zone-2", risk_score: 82, risk_band: "critical", actions: ["Procure reserve"] },
        ]);
      }
      return jsonResponse([
        {
          timestamp: "2024-01-01T18:30:00",
          zone: "Zone-2",
          forecast_kwh: 99,
          capacity_kwh: 100,
          risk_score: 82,
          risk_band: "critical",
        },
      ]);
    }),
  );
});

afterEach(() => {
  vi.unstubAllGlobals();
});

it("renders the dashboard after loading data, with no a11y violations", async () => {
  const { container } = render(<App />);

  expect(await screen.findByRole("heading", { name: "GridPulse", level: 1 })).toBeInTheDocument();
  await waitFor(() =>
    expect(screen.getByRole("heading", { name: /risk ranking/i })).toBeInTheDocument(),
  );
  expect(screen.getByText(/API v0.1.0/)).toBeInTheDocument();
  expect(await a11yViolations(container)).toEqual([]);
});
