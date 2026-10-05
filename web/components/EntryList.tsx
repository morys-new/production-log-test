"use client";

import { useState } from "react";
import type { Entry, EntryStatus, Pit } from "@/types/api";
import { formatDate, formatTonnes, formatVariance } from "@/lib/format";
import {
  MATERIAL_LABELS,
  SHIFT_LABELS,
  STATUSES,
  STATUS_LABELS,
} from "@/lib/labels";

type StatusFilter = EntryStatus | "all";

const STATUS_FILTERS: readonly StatusFilter[] = ["all", ...STATUSES];
const ALL_PITS = "all";

interface EntryListProps {
  entries: Entry[];
  pits: Pit[];
}

export function EntryList({ entries, pits }: EntryListProps) {
  const [status, setStatus] = useState<StatusFilter>("all");
  const [pitId, setPitId] = useState(ALL_PITS);

  // Filters run over the entries already loaded, so changing them never re-fetches.
  const inPit =
    pitId === ALL_PITS ? entries : entries.filter((entry) => entry.pit_id === pitId);
  const visible =
    status === "all" ? inPit : inPit.filter((entry) => entry.status === status);
  const countFor = (filter: StatusFilter): number =>
    filter === "all"
      ? inPit.length
      : inPit.filter((entry) => entry.status === filter).length;

  return (
    <>
      <div className="toolbar">
        <div className="segmented" role="group" aria-label="Filter by status">
          {STATUS_FILTERS.map((filter) => (
            <button
              key={filter}
              type="button"
              className={status === filter ? "active" : undefined}
              aria-pressed={status === filter}
              onClick={() => setStatus(filter)}
            >
              {filter === "all" ? "All" : STATUS_LABELS[filter]}
              <span className="count">{countFor(filter)}</span>
            </button>
          ))}
        </div>
        <label className="inline-field">
          Pit
          <select value={pitId} onChange={(event) => setPitId(event.target.value)}>
            <option value={ALL_PITS}>All pits</option>
            {pits.map((pit) => (
              <option key={pit.id} value={pit.id}>
                {pit.name}
              </option>
            ))}
          </select>
        </label>
      </div>
      <p className="muted small">
        Showing {visible.length} of {entries.length} entries
      </p>

      {visible.length === 0 ? (
        <p className="empty">No entries match these filters.</p>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Pit</th>
                <th>Shift</th>
                <th>Material</th>
                <th className="num">Planned (t)</th>
                <th className="num">Actual (t)</th>
                <th className="num">Variance (t)</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {visible.map((entry) => {
                const variance = entry.actual_tonnes - entry.planned_tonnes;
                return (
                  <tr key={entry.id}>
                    <td>{formatDate(entry.report_date)}</td>
                    <td>{entry.pit_name}</td>
                    <td>{SHIFT_LABELS[entry.shift]}</td>
                    <td>{MATERIAL_LABELS[entry.material]}</td>
                    <td className="num">{formatTonnes(entry.planned_tonnes)}</td>
                    <td className="num">{formatTonnes(entry.actual_tonnes)}</td>
                    <td className={`num ${variance < 0 ? "tone-bad" : ""}`}>
                      {formatVariance(variance)}
                    </td>
                    <td>
                      <span className={`badge badge-${entry.status}`}>
                        {STATUS_LABELS[entry.status]}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}
