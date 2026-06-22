const BANDS = ["low", "medium", "high", "critical"];

export function RiskBadge({ band }: { band: string }) {
  const safe = BANDS.includes(band) ? band : "low";
  return (
    <span className={`badge band-${safe}`}>
      <span className="badge-dot" aria-hidden="true" />
      {band}
    </span>
  );
}
