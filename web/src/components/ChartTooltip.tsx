interface TooltipItem {
  name?: string | number;
  value?: string | number;
  color?: string;
}

interface ChartTooltipProps {
  active?: boolean;
  label?: string | number;
  payload?: TooltipItem[];
}

const fmt = (value: string | number | undefined): string =>
  typeof value === "number" ? Math.round(value).toLocaleString("en-US") : String(value ?? "");

/** Dark, themed tooltip for the recharts charts. */
export function ChartTooltip({ active, label, payload }: ChartTooltipProps) {
  if (!active || !payload || payload.length === 0) {
    return null;
  }
  return (
    <div className="chart-tooltip">
      {label !== undefined && label !== "" && <div className="tt-title">{String(label)}</div>}
      {payload.map((item) => (
        <div className="tt-row" key={String(item.name)}>
          <span className="tt-swatch" style={{ background: item.color }} aria-hidden="true" />
          <span>{item.name}</span>
          <strong className="num">{fmt(item.value)}</strong>
        </div>
      ))}
    </div>
  );
}
