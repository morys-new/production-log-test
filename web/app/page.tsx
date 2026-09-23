"use client";

import { useEffect, useState } from "react";
import type { HealthResponse } from "../../shared/types";
import { apiFetch, ApiError } from "@/lib/api";

export default function HomePage() {
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
    <main style={{ maxWidth: 800, margin: "0 auto", padding: "2rem" }}>
      <h1>ProdLog</h1>
      {error ? (
        <p style={{ color: "red" }}>Backend unreachable: {error}</p>
      ) : health ? (
        <p>Backend: {health.status} — {health.db_version}</p>
      ) : (
        <p>Checking backend…</p>
      )}
    </main>
  );
}
