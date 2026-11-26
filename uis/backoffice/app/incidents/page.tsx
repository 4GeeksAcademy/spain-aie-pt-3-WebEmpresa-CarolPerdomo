"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { apiFetch } from "@/lib/auth-client";
import {
  INCIDENT_BRANCHES,
  INCIDENT_CATEGORIES,
  INCIDENT_ORIGINS,
  INCIDENT_STATUSES,
  incidentLabel,
  incidentMessage,
  type Incident,
  type IncidentStatus,
} from "@/lib/incidents";

const fieldClass = "rounded-lg border border-line bg-white px-3 py-2.5 text-sm outline-none focus:border-pine focus:ring-2 focus:ring-pine/15";
const transitions: Record<IncidentStatus, IncidentStatus[]> = {
  open: ["in_progress", "discarded"],
  in_progress: ["resolved", "discarded"],
  resolved: [],
  discarded: [],
};

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [filters, setFilters] = useState({ status: "", origin: "", branch: "", category: "" });
  const [loading, setLoading] = useState(true);
  const [updatingId, setUpdatingId] = useState<number | null>(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const query = useMemo(() => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => { if (value) params.set(key, value); });
    return params.toString();
  }, [filters]);

  const loadIncidents = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const response = await apiFetch(`/api/incidents${query ? `?${query}` : ""}`);
      const body: unknown = await response.json().catch(() => null);
      if (!response.ok) throw new Error(incidentMessage(body, "No se pudo cargar el listado de incidencias."));
      if (!Array.isArray(body)) throw new Error("El servidor devolvió una respuesta no válida.");
      setIncidents(body as Incident[]);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "No se pudo cargar el listado de incidencias.");
    } finally {
      setLoading(false);
    }
  }, [query]);

  useEffect(() => {
    const timer = window.setTimeout(() => { void loadIncidents(); }, 0);
    return () => window.clearTimeout(timer);
  }, [loadIncidents]);

  async function changeStatus(incident: Incident, nextStatus: string) {
    if (!transitions[incident.status].includes(nextStatus as IncidentStatus)) return;
    setUpdatingId(incident.id);
    setError("");
    setNotice("");
    try {
      const response = await apiFetch(`/api/incidents/${incident.id}/status`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: nextStatus }),
      });
      const body: unknown = await response.json().catch(() => null);
      if (!response.ok) throw new Error(incidentMessage(body, "No se pudo actualizar el estado."));
      setNotice("Estado de la incidencia actualizado.");
      await loadIncidents();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "No se pudo actualizar el estado.");
    } finally {
      setUpdatingId(null);
    }
  }

  return (
    <main className="min-h-screen px-5 py-8 sm:px-8 lg:px-12">
      <div className="mx-auto max-w-7xl">
        <header className="flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-muted">Operaciones · Registro central</p>
            <h1 className="mt-2 font-display text-4xl text-ink sm:text-5xl">Incidencias</h1>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-muted">Consulta los casos registrados y actualiza su estado según el ciclo de vida.</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Link href="/incidents/summary" className="rounded-lg border border-line bg-white px-4 py-2.5 text-sm font-semibold text-ink hover:bg-paper">Ver resumen</Link>
            <Link href="/incidents/new" className="rounded-lg bg-pine px-4 py-2.5 text-sm font-semibold text-white hover:bg-pine/90">+ Nueva incidencia</Link>
          </div>
        </header>

        {error && <div role="alert" className="mt-6 flex flex-wrap items-center justify-between gap-3 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800"><span>{error}</span><button onClick={() => void loadIncidents()} className="font-semibold underline">Reintentar</button></div>}
        {notice && <p role="status" className="mt-6 rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">{notice}</p>}

        <section aria-label="Filtros de incidencias" className="mt-7 grid gap-4 rounded-2xl border border-line bg-white p-5 sm:grid-cols-2 lg:grid-cols-4">
          <label className="text-sm font-medium">Estado<select className={`${fieldClass} mt-1 w-full`} value={filters.status} onChange={(event) => setFilters({ ...filters, status: event.target.value })}><option value="">Todos</option>{INCIDENT_STATUSES.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label>
          <label className="text-sm font-medium">Origen<select className={`${fieldClass} mt-1 w-full`} value={filters.origin} onChange={(event) => setFilters({ ...filters, origin: event.target.value })}><option value="">Todos</option>{INCIDENT_ORIGINS.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label>
          <label className="text-sm font-medium">Sede<select className={`${fieldClass} mt-1 w-full`} value={filters.branch} onChange={(event) => setFilters({ ...filters, branch: event.target.value })}><option value="">Todas</option>{INCIDENT_BRANCHES.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label>
          <label className="text-sm font-medium">Categoría<select className={`${fieldClass} mt-1 w-full`} value={filters.category} onChange={(event) => setFilters({ ...filters, category: event.target.value })}><option value="">Todas</option>{INCIDENT_CATEGORIES.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label>
        </section>

        <section aria-label="Listado de incidencias" className="mt-5 overflow-hidden rounded-2xl border border-line bg-white shadow-sm">
          {loading ? <p role="status" className="p-8 text-sm text-muted">Cargando incidencias…</p>
            : error ? <p className="p-8 text-sm text-muted">No se pudo actualizar la lista. Usa «Reintentar» para volver a cargarla.</p>
              : incidents.length === 0 ? <div className="p-8"><h2 className="font-display text-xl text-ink">No hay incidencias para mostrar</h2><p className="mt-1 text-sm text-muted">Prueba con otros filtros o registra una incidencia nueva.</p><Link href="/incidents/new" className="mt-4 inline-block text-sm font-semibold text-pine underline">Registrar incidencia</Link></div>
                : <div className="overflow-x-auto"><table className="w-full min-w-[1050px] border-collapse text-left text-sm">
                  <thead className="bg-pine text-xs uppercase tracking-wide text-white"><tr><th className="px-5 py-4">Incidencia</th><th className="px-5 py-4">Categoría</th><th className="px-5 py-4">Origen</th><th className="px-5 py-4">Sede</th><th className="px-5 py-4">Creada</th><th className="px-5 py-4">Estado y acción</th></tr></thead>
                  <tbody className="divide-y divide-line">{incidents.map((incident) => {
                    const available = transitions[incident.status];
                    return <tr key={incident.id}>
                      <td className="max-w-md px-5 py-4"><p className="font-semibold text-ink">{incident.title}</p><p className="mt-1 line-clamp-2 text-xs leading-5 text-muted">{incident.description}</p><span className="mt-1 block text-[11px] text-muted">ID {incident.id}</span></td>
                      <td className="px-5 py-4">{incidentLabel(incident.category, INCIDENT_CATEGORIES)}</td>
                      <td className="px-5 py-4">{incidentLabel(incident.origin, INCIDENT_ORIGINS)}</td>
                      <td className="px-5 py-4">{incidentLabel(incident.branch, INCIDENT_BRANCHES)}</td>
                      <td className="px-5 py-4 whitespace-nowrap">{new Date(incident.created_at).toLocaleString("es-ES", { dateStyle: "medium", timeStyle: "short", timeZone: "UTC" })} UTC</td>
                      <td className="px-5 py-4"><span className="mb-2 block font-semibold text-ink">{incidentLabel(incident.status, INCIDENT_STATUSES)}</span>{available.length > 0 ? <select aria-label={`Cambiar estado de la incidencia ${incident.id}`} className={fieldClass} disabled={updatingId === incident.id} value="" onChange={(event) => void changeStatus(incident, event.target.value)}><option value="">{updatingId === incident.id ? "Actualizando…" : "Cambiar estado"}</option>{available.map((status) => <option key={status} value={status}>{incidentLabel(status, INCIDENT_STATUSES)}</option>)}</select> : <span className="text-xs text-muted">Estado final</span>}</td>
                    </tr>;
                  })}</tbody>
                </table></div>}
        </section>
        {!loading && !error && <p className="mt-3 text-right text-sm text-muted">{incidents.length} {incidents.length === 1 ? "incidencia" : "incidencias"}</p>}
      </div>
    </main>
  );
}
