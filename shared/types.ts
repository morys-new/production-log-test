/**
 * TYPES ONLY. No runtime code.
 * Metro (Expo) and Next.js erase `import type` — this file is never bundled.
 *
 * All consumers must use:  import type { ... } from '../../shared/types'
 *
 * Mirrors the backend's Pydantic models (backend/models/). Dates are "YYYY-MM-DD",
 * timestamps are ISO 8601 strings and ids are UUID strings.
 */

export interface HealthResponse {
  status: string;
  db_version: string;
}

export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
  };
}

// ── Enumerations ─────────────────────────────────────────────────────────────

/** draft -> submitted -> approved; submitted -> draft. Approved is final. */
export type EntryStatus = "draft" | "submitted" | "approved";
export type Shift = "day" | "night";
export type Material = "ore" | "overburden";

// ── Pits ─────────────────────────────────────────────────────────────────────

/** Item of GET /pits; response of POST /pits. */
export interface Pit {
  id: string;
  name: string;
  created_at: string;
}

/** Body of POST /pits. Names are unique, ignoring case. */
export interface PitCreate {
  name: string;
}

// ── Production entries ───────────────────────────────────────────────────────

/** Item of GET /entries?status=&pit_id=; response of every /entries endpoint. */
export interface Entry {
  id: string;
  pit_id: string;
  pit_name: string;
  report_date: string;
  shift: Shift;
  material: Material;
  planned_tonnes: number;
  actual_tonnes: number;
  status: EntryStatus;
  created_at: string;
  updated_at: string;
}

/** Body of POST /entries. New entries start as draft. */
export interface EntryCreate {
  pit_id: string;
  report_date: string;
  shift: Shift;
  material: Material;
  planned_tonnes: number;
  actual_tonnes: number;
}

/** Body of PATCH /entries/{entry_id}: at least one field. Rejected once approved. */
export interface EntryNumbersUpdate {
  planned_tonnes?: number;
  actual_tonnes?: number;
}

/** Body of PATCH /entries/{entry_id}/status. */
export interface EntryStatusUpdate {
  status: EntryStatus;
}

// ── Summary ──────────────────────────────────────────────────────────────────

export type StatusCounts = Record<EntryStatus, number>;

export interface MaterialTotals {
  planned_tonnes: number;
  actual_tonnes: number;
  /** actual - planned; negative means behind plan. */
  variance_tonnes: number;
  /** actual / planned * 100; null when nothing was planned. */
  achievement_pct: number | null;
}

export interface ProductionTotals {
  entry_count: number;
  status_counts: StatusCounts;
  ore: MaterialTotals;
  overburden: MaterialTotals;
  /** Overburden tonnes per ore tonne; null without ore. */
  planned_stripping_ratio: number | null;
  actual_stripping_ratio: number | null;
}

export interface PitSummary {
  pit_id: string;
  pit_name: string;
  totals: ProductionTotals;
}

/**
 * Response of GET /summary?date_from=&date_to=. Totals include entries in every
 * status; pits without entries are listed with zeros.
 */
export interface Summary {
  date_from: string | null;
  date_to: string | null;
  totals: ProductionTotals;
  pits: PitSummary[];
}
