"use client";

import { useCallback, useEffect, useState } from "react";
import type { Entry, Pit, Summary } from "@/types/api";
import { apiFetch, ApiError } from "@/lib/api";
import { EntryForm } from "@/components/EntryForm";
import { EntryList } from "@/components/EntryList";
import { PitSummaryTable } from "@/components/PitSummaryTable";
import { SummaryCards } from "@/components/SummaryCards";

interface Dashboard {
  pits: Pit[];
  entries: Entry[];
  summary: Summary;
}

async function fetchDashboard(): Promise<Dashboard> {
  const [pits, entries, summary] = await Promise.all([
    apiFetch<Pit[]>("/pits"),
    apiFetch<Entry[]>("/entries"),
    apiFetch<Summary>("/summary"),
  ]);
  return { pits, entries, summary };
}

function errorMessage(err: unknown): string {
  return err instanceof ApiError ? err.message : "Could not reach the ProdLog API.";
}

export default function HomePage() {
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Also used to refresh after a create. It keeps the current data on screen
  // while loading, and never rejects: failures land in `error`. State is only
  // set inside promise callbacks, never synchronously in the effect below.
  const load = useCallback(
    (): Promise<void> =>
      fetchDashboard()
        .then((data) => {
          setDashboard(data);
          setError(null);
        })
        .catch((err: unknown) => setError(errorMessage(err)))
        .finally(() => setLoading(false)),
    [],
  );

  useEffect(() => {
    void load();
  }, [load]);

  function retry(): void {
    setLoading(true);
    setError(null);
    void load();
  }

  return (
    <main className="page">
      <header>
        <h1>ProdLog</h1>
        <p className="muted">Production reporting for Test Mine A</p>
      </header>

      {loading ? (
        <p className="muted" role="status">
          Loading production data…
        </p>
      ) : dashboard === null ? (
        <div className="alert alert-error" role="alert">
          <p>{error}</p>
          <button className="button button-secondary" type="button" onClick={retry}>
            Retry
          </button>
        </div>
      ) : (
        <>
          {error && (
            <div className="alert alert-error" role="alert">
              <p>Could not refresh the data: {error}</p>
              <button className="button button-secondary" type="button" onClick={retry}>
                Retry
              </button>
            </div>
          )}

          <section>
            <div className="section-head">
              <h2>Summary</h2>
              <p className="muted small">
                All dates · totals include draft and submitted entries
              </p>
            </div>
            <SummaryCards totals={dashboard.summary.totals} />
            <div className="card">
              <h3>By pit</h3>
              <PitSummaryTable pits={dashboard.summary.pits} />
            </div>
          </section>

          <div className="workspace">
            <section className="card">
              <h2>New entry</h2>
              <EntryForm pits={dashboard.pits} onCreated={load} />
            </section>
            <section className="card">
              <h2>Entries</h2>
              <EntryList entries={dashboard.entries} pits={dashboard.pits} />
            </section>
          </div>
        </>
      )}
    </main>
  );
}
