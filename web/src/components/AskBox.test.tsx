import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { a11yViolations } from "../testUtils";
import { AskBox } from "./AskBox";

function jsonResponse(body: unknown) {
  return new Response(JSON.stringify(body), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });
}

beforeEach(() => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () => jsonResponse({ answer: "Zone-2 is critical.", source: "rules" })),
  );
});

afterEach(() => {
  vi.unstubAllGlobals();
});

it("submits a question and shows the answer with its source", async () => {
  const user = userEvent.setup();
  const { container } = render(<AskBox />);

  await user.type(screen.getByLabelText("Your question"), "what is at risk?");
  await user.click(screen.getByRole("button", { name: "Ask" }));

  expect(await screen.findByText(/Zone-2 is critical/)).toBeInTheDocument();
  expect(screen.getByText(/source: rules/)).toBeInTheDocument();
  expect(await a11yViolations(container)).toEqual([]);
});

it("shows a validation error for a too-short question", async () => {
  const user = userEvent.setup();
  render(<AskBox />);

  await user.type(screen.getByLabelText("Your question"), "x");
  await user.click(screen.getByRole("button", { name: "Ask" }));

  expect(await screen.findByText(/at least 3 characters/)).toBeInTheDocument();
});
