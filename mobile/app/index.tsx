import { useEffect, useState } from "react";
import { StyleSheet, Text, View } from "react-native";
import type { HealthResponse } from "../../shared/types";
import { apiFetch, ApiError } from "../lib/api";

export default function HomeScreen() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<HealthResponse>("/health")
      .then(setHealth)
      .catch((err) =>
        setError(err instanceof ApiError ? err.message : "Unknown error"),
      );
  }, []);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>ProdLog</Text>
      {error ? (
        <Text style={styles.error}>Backend unreachable: {error}</Text>
      ) : health ? (
        <Text style={styles.status}>Backend: {health.status}</Text>
      ) : (
        <Text style={styles.status}>Checking backend...</Text>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, alignItems: "center", justifyContent: "center", padding: 24 },
  title: { fontSize: 28, fontWeight: "700", marginBottom: 16 },
  status: { fontSize: 15, color: "#555" },
  error: { fontSize: 15, color: "red" },
});
