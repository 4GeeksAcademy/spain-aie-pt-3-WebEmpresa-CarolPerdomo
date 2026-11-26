"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { apiFetch } from "@/lib/auth-client";
import {
  INCIDENT_BRANCHES,
  INCIDENT_CATEGORIES,
  INCIDENT_ORIGINS,
  INCIDENT_STATUSES,
  incidentMessage,
  type IncidentBranch,
  type IncidentCategory,
  type IncidentOrigin,
  type IncidentStatus,
} from "@/lib/incidents";

const fieldClass = "mt-1 w-full rounded-lg border border-line bg-white px-3 py-2.5 text-sm outline-none focus:border-pine focus:ring-2 focus:ring-pine/15";
const buttonClass = "rounded-lg bg-pine px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-pine/90 disabled:cursor-wait disabled:opacity-60";

export default function NewIncidentPage() {
  const [form, setForm] = useState({
    title: "", description: "", category: "technical_failure" as IncidentCategory,
    status: "open" as IncidentStatus, origin: "customer" as IncidentOrigin,
    branch: "central" as IncidentBranch,
  });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    setNotice("");
    try {
      const response = await apiFetch("/api/incidents", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      const body: unknown = await response.json().catch(() => null);
      if (!response.ok) throw new Error(incidentMessage(body, "No se pudo registrar la incidencia. Inténtalo de nuevo."));
      setForm({ title: "", description: "", category: "technical_failure", status: "open", origin: "customer", branch: "central" });
      setNotice("Incidencia registrada correctamente.");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "No se pudo registrar la incidencia. Inténtalo de nuevo.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="min-h-screen px-5 py-8 sm:px-8 lg:px-12">
      <div className="mx-auto max-w-4xl">
        <Link href="/incidents" className="text-sm font-semibold text-pine hover:underline">← Volver a incidencias</Link>
        <header className="mt-7">
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-muted">Operaciones · Incidencias</p>
          <h1 className="mt-2 font-display text-4xl text-ink sm:text-5xl">Registrar incidencia</h1>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-muted">Completa los datos para incorporar el caso al registro central.</p>
        </header>

        {error && <p role="alert" className="mt-6 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">{error}</p>}
        {notice && <p role="status" className="mt-6 rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">{notice} <Link href="/incidents" className="ml-2 font-semibold underline">Ver listado</Link></p>}

        <form onSubmit={submit} className="mt-7 rounded-2xl border border-line bg-white p-5 shadow-sm sm:p-7">
          <div className="grid gap-5 sm:grid-cols-2">
            <label className="text-sm font-medium sm:col-span-2">Título breve *
              <input className={fieldClass} required maxLength={120} value={form.title} onChange={(event) => setForm({ ...form, title: event.target.value })} />
            </label>
            <label className="text-sm font-medium sm:col-span-2">Descripción detallada *
              <textarea className={fieldClass} required rows={5} value={form.description} onChange={(event) => setForm({ ...form, description: event.target.value })} />
            </label>
            <label className="text-sm font-medium">Categoría *
              <select className={fieldClass} required value={form.category} onChange={(event) => setForm({ ...form, category: event.target.value as IncidentCategory })}>
                {INCIDENT_CATEGORIES.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
              </select>
            </label>
            <label className="text-sm font-medium">Estado inicial *
              <select className={fieldClass} required value={form.status} onChange={(event) => setForm({ ...form, status: event.target.value as IncidentStatus })}>
                {INCIDENT_STATUSES.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
              </select>
            </label>
            <label className="text-sm font-medium">Origen del reporte *
              <select className={fieldClass} required value={form.origin} onChange={(event) => setForm({ ...form, origin: event.target.value as IncidentOrigin })}>
                {INCIDENT_ORIGINS.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
              </select>
            </label>
            <label className={`rounded-lg p-2 text-sm font-medium transition-colors ${form.origin === "branch" ? "bg-orange-50 ring-1 ring-coral/40" : ""}`}>Sede *
              <select className={fieldClass} required value={form.branch} onChange={(event) => setForm({ ...form, branch: event.target.value as IncidentBranch })}>
                {INCIDENT_BRANCHES.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
              </select>
              {form.origin === "branch" && <span className="mt-1 block text-xs text-muted">Selecciona la oficina desde la que se reporta la incidencia.</span>}
            </label>
          </div>
          <div className="mt-6 flex flex-wrap items-center gap-3">
            <button type="submit" className={buttonClass} disabled={busy}>{busy ? "Guardando…" : "Registrar incidencia"}</button>
            <Link href="/incidents" className="rounded-lg border border-line px-4 py-2.5 text-sm font-semibold text-ink hover:bg-paper">Cancelar</Link>
          </div>
          <p className="sr-only" aria-live="polite">{busy ? "Guardando la incidencia" : ""}</p>
        </form>
      </div>
    </main>
  );
}
