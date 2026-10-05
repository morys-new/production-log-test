import { useCallback, useEffect, useState } from "react";
import {
  ActivityIndicator,
  FlatList,
  Pressable,
  RefreshControl,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import type { Entry, EntryStatus } from "../../shared/types";
import { apiFetch, ApiError } from "../lib/api";
import { formatDate, formatTonnes, formatVariance } from "../lib/format";
import { MATERIAL_LABELS, SHIFT_LABELS, STATUSES, STATUS_LABELS } from "../lib/labels";

type StatusFilter = EntryStatus | "all";

const STATUS_FILTERS: readonly StatusFilter[] = ["all", ...STATUSES];

function errorMessage(err: unknown): string {
  return err instanceof ApiError ? err.message : "Could not reach the ProdLog API.";
}

function Figure({
  label,
  value,
  negative = false,
}: {
  label: string;
  value: string;
  negative?: boolean;
}) {
  return (
    <View style={styles.figure}>
      <Text style={styles.figureLabel}>{label}</Text>
      <Text style={[styles.figureValue, negative && styles.negative]}>{value}</Text>
    </View>
  );
}

function EntryCard({ entry }: { entry: Entry }) {
  const variance = entry.actual_tonnes - entry.planned_tonnes;
  return (
    <View style={styles.card}>
      <View style={styles.cardHeader}>
        <Text style={styles.pit}>{entry.pit_name}</Text>
        <Text style={[styles.badge, badgeStyles[entry.status]]}>
          {STATUS_LABELS[entry.status]}
        </Text>
      </View>
      <Text style={styles.meta}>
        {formatDate(entry.report_date)} · {SHIFT_LABELS[entry.shift]} shift ·{" "}
        {MATERIAL_LABELS[entry.material]}
      </Text>
      <View style={styles.figures}>
        <Figure label="Planned" value={`${formatTonnes(entry.planned_tonnes)} t`} />
        <Figure label="Actual" value={`${formatTonnes(entry.actual_tonnes)} t`} />
        <Figure
          label="Variance"
          value={`${formatVariance(variance)} t`}
          negative={variance < 0}
        />
      </View>
    </View>
  );
}

export default function EntriesScreen() {
  const insets = useSafeAreaInsets();
  const [entries, setEntries] = useState<Entry[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [status, setStatus] = useState<StatusFilter>("all");

  // Used for the first load, pull-to-refresh and retry. It never rejects
  // (failures land in `error`) and only sets state inside promise callbacks.
  const load = useCallback(
    (): Promise<void> =>
      apiFetch<Entry[]>("/entries")
        .then((data) => {
          setEntries(data);
          setError(null);
        })
        .catch((err: unknown) => setError(errorMessage(err))),
    [],
  );

  useEffect(() => {
    void load();
  }, [load]);

  function refresh(): void {
    setRefreshing(true);
    void load().finally(() => setRefreshing(false));
  }

  function retry(): void {
    setError(null);
    void load();
  }

  if (entries === null) {
    return (
      <View style={styles.centered}>
        {error === null ? (
          <ActivityIndicator size="large" accessibilityLabel="Loading entries" />
        ) : (
          <>
            <Text style={styles.errorText}>{error}</Text>
            <Pressable style={styles.retry} accessibilityRole="button" onPress={retry}>
              <Text style={styles.retryText}>Retry</Text>
            </Pressable>
          </>
        )}
      </View>
    );
  }

  // Filtering runs over the loaded list, so switching status never re-fetches.
  const visible =
    status === "all" ? entries : entries.filter((entry) => entry.status === status);
  const countFor = (filter: StatusFilter): number =>
    filter === "all"
      ? entries.length
      : entries.filter((entry) => entry.status === filter).length;

  return (
    <View style={styles.screen}>
      <View style={styles.filters}>
        {STATUS_FILTERS.map((filter) => {
          const selected = status === filter;
          return (
            <Pressable
              key={filter}
              accessibilityRole="button"
              accessibilityState={{ selected }}
              onPress={() => setStatus(filter)}
              style={[styles.chip, selected && styles.chipSelected]}
            >
              <Text style={[styles.chipText, selected && styles.chipTextSelected]}>
                {filter === "all" ? "All" : STATUS_LABELS[filter]} {countFor(filter)}
              </Text>
            </Pressable>
          );
        })}
      </View>

      {error !== null && (
        <Text style={styles.banner}>Could not refresh: {error}</Text>
      )}

      <FlatList
        data={visible}
        keyExtractor={(entry) => entry.id}
        renderItem={({ item }) => <EntryCard entry={item} />}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={refresh} />}
        contentContainerStyle={[styles.list, { paddingBottom: insets.bottom + 16 }]}
        ListEmptyComponent={
          <Text style={styles.empty}>
            {status === "all"
              ? "No entries yet."
              : `No ${STATUS_LABELS[status].toLowerCase()} entries.`}
          </Text>
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: "#f5f6f8" },
  centered: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    padding: 24,
    gap: 12,
    backgroundColor: "#f5f6f8",
  },
  errorText: { fontSize: 15, color: "#c62828", textAlign: "center" },
  retry: {
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: "#1f5fbf",
  },
  retryText: { color: "#1f5fbf", fontWeight: "600" },
  filters: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 6,
    paddingHorizontal: 16,
    paddingTop: 12,
    paddingBottom: 8,
  },
  chip: {
    paddingVertical: 6,
    paddingHorizontal: 10,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: "#dde1e7",
    backgroundColor: "#ffffff",
  },
  chipSelected: { backgroundColor: "#1f5fbf", borderColor: "#1f5fbf" },
  chipText: { fontSize: 13, color: "#17202b" },
  chipTextSelected: { color: "#ffffff", fontWeight: "600" },
  banner: {
    marginHorizontal: 16,
    marginBottom: 8,
    padding: 10,
    borderRadius: 8,
    backgroundColor: "#fdecec",
    color: "#8a1c1c",
  },
  list: { paddingHorizontal: 16, paddingTop: 4, gap: 10 },
  empty: { textAlign: "center", color: "#5d6877", paddingVertical: 32 },
  card: {
    backgroundColor: "#ffffff",
    borderRadius: 10,
    borderWidth: 1,
    borderColor: "#dde1e7",
    padding: 14,
    gap: 6,
  },
  cardHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    gap: 8,
  },
  pit: { fontSize: 16, fontWeight: "700", color: "#17202b" },
  badge: {
    overflow: "hidden",
    paddingVertical: 2,
    paddingHorizontal: 8,
    borderRadius: 999,
    fontSize: 12,
    fontWeight: "600",
  },
  meta: { fontSize: 13, color: "#5d6877" },
  figures: { flexDirection: "row", marginTop: 4 },
  figure: { flex: 1 },
  figureLabel: { fontSize: 11, color: "#5d6877", textTransform: "uppercase" },
  figureValue: { fontSize: 15, fontWeight: "600", color: "#17202b" },
  negative: { color: "#c62828" },
});

const badgeStyles = StyleSheet.create({
  draft: { backgroundColor: "#eceff3", color: "#44505f" },
  submitted: { backgroundColor: "#fff1cc", color: "#6f4a00" },
  approved: { backgroundColor: "#d9f2e1", color: "#155f35" },
});
