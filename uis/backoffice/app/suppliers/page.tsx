"use client";

import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { apiFetch } from "@/lib/auth-client";

type Supplier = {
  id: number;
  name: string;
  country: "Spain" | "USA";
  categories: string[];
  monthly_rate: number;
  currency: "EUR" | "USD";
  status: "active" | "suspended";
  updated_at?: string | null;
  contract_renewal_date?: string | null;
  contact_email?: string | null;
  notes?: string | null;
};

const categories = [
  ["job_boards", "Portales de empleo"],
  ["ats_software", "Software ATS"],
  ["assessment_tools", "Evaluación"],
  ["training_platforms", "Formación"],
  ["payroll_and_hr_software", "Nómina y RR. HH."],
  ["video_interview", "Entrevistas por vídeo"],
  ["background_check", "Verificación de antecedentes"],
  ["office_and_facilities", "Oficina e instalaciones"],
  ["it_and_software_licenses", "TI y licencias"],
] as const;

const inputClass = "mt-1 w-full rounded-lg border border-line bg-white px-3 py-2.5 text-sm outline-none focus:border-pine focus:ring-2 focus:ring-pine/15";
const buttonClass = "rounded-lg bg-pine px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-pine/90 disabled:cursor-wait disabled:opacity-60";

function messageFrom(body: unknown, fallback: string) {
  if (body && typeof body === "object" && "detail" in body && typeof body.detail === "string") return body.detail;
  return fallback;
}

function isRenewalSoon(value?: string | null) {
  if (!value) return false;
  const renewal = new Date(`${value}T00:00:00`);
  if (Number.isNaN(renewal.getTime())) return false;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const daysUntil = Math.ceil((renewal.getTime() - today.getTime()) / 86_400_000);
  return daysUntil >= 0 && daysUntil <= 60;
}

function formatTimestamp(value?: string | null) {
  if (!value) return "N/D";
  const timestamp = new Date(value);
  return Number.isNaN(timestamp.getTime())
    ? "?"
    : timestamp.toLocaleString("es-ES", { dateStyle: "short", timeStyle: "short" });
}

export default function SuppliersPage() {
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [country, setCountry] = useState("");
  const [category, setCategory] = useState("");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [rate, setRate] = useState("");
  const [form, setForm] = useState({
    name: "", country: "Spain" as "Spain" | "USA", currency: "EUR" as "EUR" | "USD",
    monthly_rate: "", categories: [] as string[], status: "active" as "active" | "suspended",
    contact_email: "", contract_renewal_date: "", notes: "",
  });

  const query = useMemo(() => {
    const params = new URLSearchParams();
    if (country) params.set("country", country);
    if (category) params.set("category", category);
    return params.toString();
  }, [country, category]);

  const loadSuppliers = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const response = await apiFetch(`/api/suppliers${query ? `?${query}` : ""}`);
      const body: unknown = await response.json().catch(() => null);
      if (!response.ok) {
        throw new Error(messageFrom(body, `No se pudo cargar el directorio (HTTP ${response.status}).`));
      }
      if (!Array.isArray(body)) throw new Error("El servidor devolvió una respuesta no válida.");
      setSuppliers(body as Supplier[]);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "No se pudo cargar el directorio.");
    } finally {
      setLoading(false);
    }
  }, [query]);

  useEffect(() => {
    const timer = window.setTimeout(() => { void loadSuppliers(); }, 0);
    return () => window.clearTimeout(timer);
  }, [loadSuppliers]);

  async function send(path: string, init: RequestInit, success: string) {
    setBusy(true);
    setError("");
    setNotice("");
    try {
      const response = await apiFetch(path, init);
      const body = response.status === 204 ? null : await response.json().catch(() => null);
      if (!response.ok) throw new Error(messageFrom(body, "No se pudo completar la operación."));
      setNotice(success);
      await loadSuppliers();
      return true;
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "No se pudo completar la operación.");
      return false;
    } finally {
      setBusy(false);
    }
  }

  async function createSupplier(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const ok = await send("/api/suppliers", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...form, monthly_rate: Number(form.monthly_rate), contract_renewal_date: form.contract_renewal_date || null, contact_email: form.contact_email || null, notes: form.notes || null }),
    }, "Proveedor registrado.");
    if (ok) {
      setShowForm(false);
      setForm({ name: "", country: "Spain", currency: "EUR", monthly_rate: "", categories: [], status: "active", contact_email: "", contract_renewal_date: "", notes: "" });
    }
  }

  async function saveRate(id: number) {
    const amount = Number(rate);
    if (!Number.isFinite(amount) || amount <= 0) { setError("La tarifa debe ser mayor que cero."); return; }
    if (await send(`/api/suppliers/${id}/rate`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ monthly_rate: amount }) }, "Tarifa actualizada.")) setEditingId(null);
  }

  async function toggleStatus(supplier: Supplier) {
    const nextStatus = supplier.status === "active" ? "suspended" : "active";
    await send(`/api/suppliers/${supplier.id}/status`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ status: nextStatus }) }, nextStatus === "active" ? "Proveedor activado." : "Proveedor suspendido.");
  }

  function toggleCategory(value: string) {
    setForm((current) => ({ ...current, categories: current.categories.includes(value) ? current.categories.filter((item) => item !== value) : [...current.categories, value] }));
  }

  return (
    <main className="min-h-screen px-5 py-8 sm:px-8 lg:px-12">
      <div className="mx-auto max-w-7xl">
        <Link href="/" className="text-sm font-semibold text-pine hover:underline">← Volver al resumen</Link>
        <header className="mt-7 flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-muted">Operaciones · Directorio</p>
            <h1 className="mt-2 font-display text-4xl text-ink sm:text-5xl">Proveedores</h1>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-muted">Consulta y administra proveedores, tarifas mensuales y estado de servicio.</p>
          </div>
          <button className={buttonClass} onClick={() => setShowForm((visible) => !visible)}>{showForm ? "Cerrar formulario" : "+ Nuevo proveedor"}</button>
        </header>

        {error && <p role="alert" className="mt-6 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">{error}</p>}
        {notice && <p role="status" className="mt-6 rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">{notice}</p>}

        {showForm && <form onSubmit={createSupplier} className="mt-8 rounded-2xl border border-line bg-white p-5 shadow-sm sm:p-7">
          <h2 className="font-display text-2xl">Registrar proveedor</h2>
          <div className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <label className="text-sm font-medium">Nombre *<input className={inputClass} required minLength={1} value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></label>
            <label className="text-sm font-medium">País *<select className={inputClass} value={form.country} onChange={(e) => { const next = e.target.value as "Spain" | "USA"; setForm({ ...form, country: next, currency: next === "Spain" ? "EUR" : "USD" }); }}><option value="Spain">España</option><option value="USA">Estados Unidos</option></select></label>
            <label className="text-sm font-medium">Tarifa mensual *<input className={inputClass} required type="number" min="0.01" step="0.01" value={form.monthly_rate} onChange={(e) => setForm({ ...form, monthly_rate: e.target.value })} /></label>
            <label className="text-sm font-medium">Moneda<select className={inputClass} value={form.currency} disabled><option value="EUR">EUR</option><option value="USD">USD</option></select></label>
            <label className="text-sm font-medium">Estado<select className={inputClass} value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value as "active" | "suspended" })}><option value="active">Activo</option><option value="suspended">Suspendido</option></select></label>
            <label className="text-sm font-medium">Email de contacto<input className={inputClass} type="email" value={form.contact_email} onChange={(e) => setForm({ ...form, contact_email: e.target.value })} /></label>
            <label className="text-sm font-medium">Renovación del contrato<input className={inputClass} type="date" value={form.contract_renewal_date} onChange={(e) => setForm({ ...form, contract_renewal_date: e.target.value })} /></label>
            <fieldset className="sm:col-span-2 lg:col-span-3">
              <legend className="text-sm font-medium">Categorías *</legend>
              <div className="mt-2 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">{categories.map(([value, label]) => <label key={value} className="flex items-center gap-2 text-sm text-muted"><input type="checkbox" checked={form.categories.includes(value)} onChange={() => toggleCategory(value)} />{label}</label>)}</div>
              {form.categories.length === 0 && <p className="mt-1 text-xs text-muted">Selecciona al menos una categoría.</p>}
            </fieldset>
            <label className="text-sm font-medium sm:col-span-2 lg:col-span-3">Notas<textarea className={inputClass} rows={3} value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} /></label>
          </div>
          <button className={`${buttonClass} mt-5`} disabled={busy || form.categories.length === 0}>{busy ? "Guardando…" : "Guardar proveedor"}</button>
        </form>}

        <section aria-label="Filtros de proveedores" className="mt-8 flex flex-col gap-4 rounded-2xl border border-line bg-white p-5 sm:flex-row sm:items-end">
          <label className="text-sm font-medium">País<select className={inputClass} value={country} onChange={(e) => setCountry(e.target.value)}><option value="">Todos los países</option><option value="Spain">España</option><option value="USA">Estados Unidos</option></select></label>
          <label className="text-sm font-medium sm:min-w-72">Categoría<select className={inputClass} value={category} onChange={(e) => setCategory(e.target.value)}><option value="">Todas las categorías</option>{categories.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label>
          <p className="text-sm text-muted sm:ml-auto">{loading ? "Actualizando…" : `${suppliers.length} ${suppliers.length === 1 ? "proveedor" : "proveedores"}`}</p>
        </section>

        <section className="mt-5 overflow-hidden rounded-2xl border border-line bg-white shadow-sm" aria-label="Listado de proveedores">
          {loading ? <p className="p-8 text-sm text-muted">Cargando proveedores…</p> : suppliers.length === 0 ? <p className="p-8 text-sm text-muted">No hay proveedores para estos filtros.</p> : <div className="overflow-x-auto">
            <table className="w-full min-w-[1120px] border-collapse text-left text-sm">
              <thead className="bg-pine text-xs uppercase tracking-wide text-white"><tr><th className="px-5 py-4">Proveedor</th><th className="px-5 py-4">País</th><th className="px-5 py-4">Categorías</th><th className="px-5 py-4">Tarifa mensual</th><th className="px-5 py-4">Estado</th><th className="px-5 py-4">Renovación</th><th className="px-5 py-4">Actualizado</th><th className="px-5 py-4">Notas</th><th className="px-5 py-4">Acciones</th></tr></thead>
              <tbody className="divide-y divide-line">{suppliers.map((supplier) => <tr key={supplier.id} className={supplier.status === "suspended" ? "bg-slate-50 text-muted" : ""}>
                <td className="px-5 py-4"><p className="font-semibold text-ink">{supplier.name}</p>{supplier.contact_email && <p className="mt-1 text-xs text-muted">{supplier.contact_email}</p>}</td>
                <td className="px-5 py-4">{supplier.country === "Spain" ? "España" : "Estados Unidos"}</td>
                <td className="max-w-64 px-5 py-4">{supplier.categories.map((item) => categories.find(([value]) => value === item)?.[1] ?? item).join(", ")}</td>
                <td className="px-5 py-4">{editingId === supplier.id ? <div className="flex items-center gap-2"><input aria-label={`Nueva tarifa para ${supplier.name}`} className="w-28 rounded border border-line px-2 py-1" type="number" min="0.01" step="0.01" value={rate} onChange={(e) => setRate(e.target.value)} /><button disabled={busy} onClick={() => void saveRate(supplier.id)} className="font-semibold text-pine underline">Guardar</button><button onClick={() => setEditingId(null)} className="text-muted underline">Cancelar</button></div> : <span>{supplier.monthly_rate.toFixed(2)} {supplier.currency} <button onClick={() => { setEditingId(supplier.id); setRate(String(supplier.monthly_rate)); }} className="ml-2 text-xs font-semibold text-pine underline">Editar</button></span>}</td>
                <td className="px-5 py-4"><span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${supplier.status === "active" ? "bg-emerald-100 text-emerald-800" : "bg-slate-200 text-slate-700"}`}>{supplier.status === "active" ? "Activo" : "Suspendido"}</span></td>
                <td className="px-5 py-4">{supplier.contract_renewal_date ? <span className="flex flex-col items-start gap-1">{supplier.contract_renewal_date}{isRenewalSoon(supplier.contract_renewal_date) && <span className="rounded-full bg-amber-100 px-2 py-0.5 text-xs font-semibold text-amber-900">Pr&oacute;xima</span>}</span> : "N/D"}</td>
                <td className="px-5 py-4 text-xs">{formatTimestamp(supplier.updated_at)}</td>
                <td className="max-w-64 px-5 py-4 text-xs">{supplier.notes || "N/D"}</td>
                <td className="px-5 py-4"><button disabled={busy} onClick={() => void toggleStatus(supplier)} className="font-semibold text-pine underline">{supplier.status === "active" ? "Suspender" : "Activar"}</button></td>
              </tr>)}</tbody>
            </table>
          </div>}
        </section>
      </div>
    </main>
  );
}
