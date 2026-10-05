import type { MaterialTotals, ProductionTotals } from "@/types/api";
import {
  achievementTone,
  formatPct,
  formatRatio,
  formatTonnes,
  formatVariance,
} from "@/lib/format";

function MaterialCard({ label, totals }: { label: string; totals: MaterialTotals }) {
  return (
    <div className="card stat">
      <p className="stat-label">{label}</p>
      <p className="stat-value">{formatTonnes(totals.actual_tonnes)} t</p>
      <p className="muted">of {formatTonnes(totals.planned_tonnes)} t planned</p>
      <p>
        {totals.achievement_pct === null ? (
          <span className="tone-neutral">No plan set</span>
        ) : (
          <span className={`tone-${achievementTone(totals.achievement_pct)}`}>
            {formatPct(totals.achievement_pct)} of plan
          </span>
        )}
        <span className="muted"> · {formatVariance(totals.variance_tonnes)} t</span>
      </p>
    </div>
  );
}

export function SummaryCards({ totals }: { totals: ProductionTotals }) {
  const counts = totals.status_counts;
  return (
    <div className="stats">
      <MaterialCard label="Ore mined" totals={totals.ore} />
      <MaterialCard label="Overburden removed" totals={totals.overburden} />
      <div className="card stat">
        <p className="stat-label">Stripping ratio</p>
        <p className="stat-value">{formatRatio(totals.actual_stripping_ratio)}</p>
        <p className="muted">
          plan {formatRatio(totals.planned_stripping_ratio)} · t overburden per t ore
        </p>
      </div>
      <div className="card stat">
        <p className="stat-label">Entries</p>
        <p className="stat-value">{totals.entry_count}</p>
        <p className="muted">
          {counts.submitted} awaiting approval · {counts.draft} draft ·{" "}
          {counts.approved} approved
        </p>
      </div>
    </div>
  );
}
