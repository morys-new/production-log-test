import type { MaterialTotals, PitSummary } from "@/types/api";
import { achievementTone, formatPct, formatRatio, formatTonnes } from "@/lib/format";

function MaterialCells({ totals }: { totals: MaterialTotals }) {
  return (
    <>
      <td className="num">
        {formatTonnes(totals.actual_tonnes)} / {formatTonnes(totals.planned_tonnes)}
      </td>
      <td className={`num tone-${achievementTone(totals.achievement_pct)}`}>
        {formatPct(totals.achievement_pct)}
      </td>
    </>
  );
}

export function PitSummaryTable({ pits }: { pits: PitSummary[] }) {
  if (pits.length === 0) {
    return <p className="empty">No pits yet.</p>;
  }
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Pit</th>
            <th className="num">Ore actual / plan (t)</th>
            <th className="num">Ore %</th>
            <th className="num">Overburden actual / plan (t)</th>
            <th className="num">OB %</th>
            <th className="num">Strip ratio (plan)</th>
            <th className="num">Not yet approved</th>
          </tr>
        </thead>
        <tbody>
          {pits.map(({ pit_id, pit_name, totals }) => (
            <tr key={pit_id}>
              <td>{pit_name}</td>
              <MaterialCells totals={totals.ore} />
              <MaterialCells totals={totals.overburden} />
              <td className="num">
                {formatRatio(totals.actual_stripping_ratio)} (
                {formatRatio(totals.planned_stripping_ratio)})
              </td>
              <td className="num">
                {totals.status_counts.draft + totals.status_counts.submitted}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
