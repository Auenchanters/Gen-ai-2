import { render, screen } from "@testing-library/react";
import { expect, it } from "vitest";
import { a11yViolations } from "../testUtils";
import { DataTable } from "./DataTable";

interface Row {
  name: string;
  value: number;
}

it("renders caption, headers, and rows with no a11y violations", async () => {
  const { container } = render(
    <DataTable<Row>
      caption="Sample table"
      rowKey={(row) => row.name}
      rows={[
        { name: "A", value: 1 },
        { name: "B", value: 2 },
      ]}
      columns={[
        { key: "name", label: "Name" },
        { key: "value", label: "Value" },
      ]}
    />,
  );

  expect(screen.getByRole("table", { name: "Sample table" })).toBeInTheDocument();
  expect(screen.getByRole("columnheader", { name: "Name" })).toBeInTheDocument();
  expect(screen.getByRole("cell", { name: "A" })).toBeInTheDocument();
  expect(await a11yViolations(container)).toEqual([]);
});
