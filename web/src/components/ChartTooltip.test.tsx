import { render, screen } from "@testing-library/react";
import { expect, it } from "vitest";
import { ChartTooltip } from "./ChartTooltip";

it("renders nothing when inactive", () => {
  const { container } = render(<ChartTooltip active={false} payload={[]} />);
  expect(container).toBeEmptyDOMElement();
});

it("renders the label and payload rows when active", () => {
  render(
    <ChartTooltip
      active
      label="Zone-1"
      payload={[{ name: "Risk score", value: 82, color: "#f85149" }]}
    />,
  );
  expect(screen.getByText("Zone-1")).toBeInTheDocument();
  expect(screen.getByText("Risk score")).toBeInTheDocument();
  expect(screen.getByText("82")).toBeInTheDocument();
});
