import type { EntryStatus, Material, Shift } from "../../shared/types";

// shared/types.ts is types-only, so the option lists live here. Record<Union, …>
// makes type-check fail if the backend adds a value we have no label for.
export const STATUSES: readonly EntryStatus[] = ["draft", "submitted", "approved"];

export const STATUS_LABELS: Record<EntryStatus, string> = {
  draft: "Draft",
  submitted: "Submitted",
  approved: "Approved",
};

export const SHIFT_LABELS: Record<Shift, string> = {
  day: "Day",
  night: "Night",
};

export const MATERIAL_LABELS: Record<Material, string> = {
  ore: "Ore",
  overburden: "Overburden",
};
