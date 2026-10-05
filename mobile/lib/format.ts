const tonnesFormat = new Intl.NumberFormat("en-US", { maximumFractionDigits: 2 });

const MONTHS = [
  "Jan",
  "Feb",
  "Mar",
  "Apr",
  "May",
  "Jun",
  "Jul",
  "Aug",
  "Sep",
  "Oct",
  "Nov",
  "Dec",
] as const;

export function formatTonnes(value: number): string {
  return tonnesFormat.format(value);
}

export function formatVariance(value: number): string {
  if (value === 0) return "0";
  const sign = value > 0 ? "+" : "−";
  return `${sign}${tonnesFormat.format(Math.abs(value))}`;
}

/** "2026-10-05" -> "5 Oct 2026". Parsed by hand, so no time zone shifts the day. */
export function formatDate(isoDate: string): string {
  const [year, month, day] = isoDate.split("-");
  return `${Number(day)} ${MONTHS[Number(month) - 1]} ${year}`;
}
