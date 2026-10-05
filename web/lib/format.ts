const tonnesFormat = new Intl.NumberFormat("en-US", { maximumFractionDigits: 2 });
const dateFormat = new Intl.DateTimeFormat("en-GB", {
  day: "numeric",
  month: "short",
  year: "numeric",
  timeZone: "UTC",
});

export function formatTonnes(value: number): string {
  return tonnesFormat.format(value);
}

export function formatVariance(value: number): string {
  if (value === 0) return "0";
  const sign = value > 0 ? "+" : "−";
  return `${sign}${tonnesFormat.format(Math.abs(value))}`;
}

export function formatPct(value: number | null): string {
  return value === null ? "—" : `${value.toFixed(1)}%`;
}

export function formatRatio(value: number | null): string {
  return value === null ? "—" : value.toFixed(2);
}

/** "2026-10-05" -> "5 Oct 2026", read as UTC so no time zone shifts the day. */
export function formatDate(isoDate: string): string {
  return dateFormat.format(new Date(`${isoDate}T00:00:00Z`));
}

/** Today in the browser's local time zone, as YYYY-MM-DD. */
export function todayIso(): string {
  const now = new Date();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  return `${now.getFullYear()}-${month}-${day}`;
}

export type Tone = "good" | "warn" | "bad" | "neutral";

/** At or above plan is good, within 10% below is a warning, further is bad. */
export function achievementTone(pct: number | null): Tone {
  if (pct === null) return "neutral";
  if (pct >= 100) return "good";
  if (pct >= 90) return "warn";
  return "bad";
}
