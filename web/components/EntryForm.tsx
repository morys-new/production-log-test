"use client";

import { useState } from "react";
import type { FormEvent } from "react";
import type { Entry, EntryCreate, Material, Pit, Shift } from "@/types/api";
import { apiFetch, ApiError } from "@/lib/api";
import { todayIso } from "@/lib/format";
import { MATERIALS, MATERIAL_LABELS, SHIFTS, SHIFT_LABELS } from "@/lib/labels";

interface EntryFormProps {
  pits: Pit[];
  /** Called after a successful create; must handle its own errors. */
  onCreated: () => Promise<void>;
}

interface FormValues {
  pitId: string;
  reportDate: string;
  shift: Shift;
  material: Material;
  planned: string;
  actual: string;
}

/** Narrows a <select> value back to its union type without a cast. */
function pick<T extends string>(options: readonly T[], value: string): T {
  return options.find((option) => option === value) ?? options[0];
}

export function EntryForm({ pits, onCreated }: EntryFormProps) {
  const [values, setValues] = useState<FormValues>(() => ({
    pitId: "",
    reportDate: todayIso(),
    shift: "day",
    material: "ore",
    planned: "",
    actual: "",
  }));
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState<string | null>(null);

  function update<K extends keyof FormValues>(key: K, value: FormValues[K]): void {
    setValues((prev) => ({ ...prev, [key]: value }));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    setSaved(null);
    const payload: EntryCreate = {
      pit_id: values.pitId,
      report_date: values.reportDate,
      shift: values.shift,
      material: values.material,
      planned_tonnes: Number(values.planned),
      actual_tonnes: Number(values.actual),
    };
    try {
      const entry = await apiFetch<Entry>("/entries", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      // Keep pit, date, shift and material: operators often log several in a row.
      setValues((prev) => ({ ...prev, planned: "", actual: "" }));
      setSaved(
        `Saved ${entry.pit_name} · ${SHIFT_LABELS[entry.shift]} shift · ` +
          `${MATERIAL_LABELS[entry.material]} as a draft.`,
      );
      await onCreated();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not reach the server.");
    } finally {
      setSubmitting(false);
    }
  }

  if (pits.length === 0) {
    return <p className="muted">No pits yet. Create one with POST /pits first.</p>;
  }

  return (
    <form className="form" onSubmit={handleSubmit}>
      <label className="field">
        Pit
        <select
          required
          value={values.pitId}
          onChange={(event) => update("pitId", event.target.value)}
        >
          <option value="" disabled>
            Select a pit
          </option>
          {pits.map((pit) => (
            <option key={pit.id} value={pit.id}>
              {pit.name}
            </option>
          ))}
        </select>
      </label>

      <label className="field">
        Report date
        <input
          type="date"
          required
          max={todayIso()}
          value={values.reportDate}
          onChange={(event) => update("reportDate", event.target.value)}
        />
      </label>

      <div className="field-row">
        <label className="field">
          Shift
          <select
            value={values.shift}
            onChange={(event) => update("shift", pick(SHIFTS, event.target.value))}
          >
            {SHIFTS.map((shift) => (
              <option key={shift} value={shift}>
                {SHIFT_LABELS[shift]}
              </option>
            ))}
          </select>
        </label>
        <label className="field">
          Material
          <select
            value={values.material}
            onChange={(event) =>
              update("material", pick(MATERIALS, event.target.value))
            }
          >
            {MATERIALS.map((material) => (
              <option key={material} value={material}>
                {MATERIAL_LABELS[material]}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="field-row">
        <label className="field">
          Planned (t)
          <input
            type="number"
            inputMode="decimal"
            required
            min={0}
            step={0.01}
            value={values.planned}
            onChange={(event) => update("planned", event.target.value)}
          />
        </label>
        <label className="field">
          Actual (t)
          <input
            type="number"
            inputMode="decimal"
            required
            min={0}
            step={0.01}
            value={values.actual}
            onChange={(event) => update("actual", event.target.value)}
          />
        </label>
      </div>

      {error && (
        <p className="form-error" role="alert">
          {error}
        </p>
      )}
      {saved && (
        <p className="form-success" role="status">
          {saved}
        </p>
      )}

      <button className="button" type="submit" disabled={submitting}>
        {submitting ? "Saving…" : "Create entry"}
      </button>
    </form>
  );
}
