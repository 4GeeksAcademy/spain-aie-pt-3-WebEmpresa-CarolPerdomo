"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { apiFetch } from "@/lib/auth-client";
import {
  INCIDENT_BRANCHES,
  INCIDENT_CATEGORIES,
  INCIDENT_ORIGINS,
  INCIDENT_STATUSES,
  incidentMessage,
  type IncidentSummary,
} from "@/lib/incidents";

function MetricGroup({ title, values, options }: { title: string; values: Record<string, number>; options: ReadonlyArray<readonly [string, string]> }) {
  return <section className="rounded-2xl border border-line bg-white p-5 shadow-sm sm:p-6">
    <h2 className="font-display text-2xl text-ink">{title}</h2>
    <dl className="mt-4 divide-y divide-line">{options.map(([value, label]) => <div key={value} className="flex items-center justify-between gap-4 py-3"><dt className="text-sm text-muted">{label}</dt><dd className="text-lg font-semibold tabular-nums text-ink">{values[value] ?? 0}</dd></div>)}</dl>
  </section>;
}

export default function IncidentSummaryPage() {
  const [summary, setSummary] = useState<IncidentSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadSummary = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const response = await apiFetch("/api/incidents/summary");
      const body: unknown = await response.json().catch(() => null);
      if (!response.ok) throw new Error(incidentMessage(body, "No se pudo cargar el resumen de incidencias."));
      setSummary(body as IncidentSummary);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "No se pudo cargar el resumen de incidencias.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const timer = window.setTimeout(() => { void loadSummary(); }, 0);
    return () => window.clearTimeout(timer);
  }, [loadSummary]);

  return <main className="min-h-screen px-5 py-8 sm:px-8 lg:px-12">
    <div className="mx-auto max-w-7xl">
      <Link href="/incidents" className="text-sm font-semibold text-pine hover:underline">← Volver a incidencias</Link>
      <header className="mt-7 flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between">
        <div><p className="text-xs font-bold uppercase tracking-[0.18em] text-muted">Operaciones · Incidencias</p><h1 className="mt-2 font-display text-4xl text-ink sm:text-5xl">Resumen</h1><p className="mt-2 text-sm leading-6 text-muted">Totales agrupados por estado, categoría, origen y sede.</p></div>
        <Link href="/incidents/new" className="w-fit rounded-lg bg-pine px-4 py-2.5 text-sm font-semibold text-white hover:bg-pine/90">+ Nueva incidencia</Link>
      </header>
      {error && <div role="alert" className="mt-6 flex flex-wrap items-center justify-between gap-3 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800"><span>{error}</span><button onClick={() => void loadSummary()} className="font-semibold underline">Reintentar</button></div>}
      {loading ? <p role="status" className="mt-8 rounded-xl border border-line bg-white p-7 text-sm text-muted">Cargando métricas…</p>
        : error ? <p className="mt-4 text-sm text-muted">Las métricas no están disponibles. El resto de la aplicación sigue funcionando.</p>
          : summary && <>
            <section className="mt-8 rounded-2xl bg-pine p-6 text-white sm:p-8"><p className="text-xs font-bold uppercase tracking-[0.18em] text-white/65">Incidencias registradas</p><p className="mt-2 font-display text-5xl">{summary.total ?? 0}</p></section>
            {summary.total === 0 ? <p className="mt-5 rounded-xl border border-line bg-white p-6 text-sm text-muted">Aún no hay incidencias registradas. Las métricas se completarán cuando se creen casos.</p> : <div className="mt-5 grid gap-5 md:grid-cols-2">
              <MetricGroup title="Por estado" values={summary.by_status ?? {}} options={INCIDENT_STATUSES} />
              <MetricGroup title="Por categoría" values={summary.by_category ?? {}} options={INCIDENT_CATEGORIES} />
              <MetricGroup title="Por origen" values={summary.by_origin ?? {}} options={INCIDENT_ORIGINS} />
              <MetricGroup title="Por sede" values={summary.by_branch ?? {}} options={INCIDENT_BRANCHES} />
            </div>}
            <p className="mt-4 text-xs text-muted">Las fechas de creación y modificación se almacenan en UTC.</p>
          </>}
    </div>
  </main>;
}
