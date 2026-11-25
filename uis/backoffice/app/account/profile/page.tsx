"use client";

import Link from "next/link";
import { useEffect, useState, type FormEvent } from "react";
import { apiFetch } from "@/lib/auth-client";
import { Sidebar } from "@/components/sidebar";

type Account = { email: string; profile: { name: string | null; phone: string | null; address: string | null } | null };
type Profile = { name: string | null; phone: string | null; address: string | null };

export default function AccountProfilePage() {
  const [email, setEmail] = useState("");
  const [profile, setProfile] = useState<Profile>({ name: "", phone: "", address: "" });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  useEffect(() => {
    let active = true;
    void apiFetch("/api/auth/me").then(async (response) => {
      const account = await response.json() as Account;
      if (!response.ok) throw new Error("No se pudo cargar la cuenta.");
      if (active) { setEmail(account.email); setProfile({ name: account.profile?.name ?? "", phone: account.profile?.phone ?? "", address: account.profile?.address ?? "" }); }
    }).catch((cause) => { if (active) setError(cause instanceof Error ? cause.message : "No se pudo cargar el perfil."); }).finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);

  async function saveProfile(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setError("");
    setNotice("");
    try {
      const response = await apiFetch("/api/profiles/me", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(profile),
      });
      const body = await response.json().catch(() => null);
      if (!response.ok) throw new Error(typeof body?.detail === "string" ? body.detail : "No se pudo guardar el perfil.");
      setNotice("Perfil actualizado.");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "No se pudo guardar el perfil.");
    } finally {
      setSaving(false);
    }
  }

  const inputClass = "mt-1 w-full rounded-lg border border-line bg-white px-3 py-2.5 text-sm outline-none focus:border-pine focus:ring-2 focus:ring-pine/15";

  return <div className="min-h-screen lg:grid lg:grid-cols-[248px_minmax(0,1fr)]">
    <Sidebar />
    <main className="min-w-0 px-4 py-8 sm:px-7 lg:px-10 lg:py-10">
      <div className="mx-auto max-w-3xl">
        <Link href="/" className="text-sm font-semibold text-pine hover:underline">← Volver al resumen</Link>
        <Link href="/account/change-password" className="ml-5 text-sm font-semibold text-pine hover:underline">Cambiar contraseña</Link>
        <header className="mt-7 border-b border-line pb-6"><p className="text-xs font-bold uppercase tracking-[0.18em] text-muted">Cuenta</p><h1 className="mt-2 font-display text-4xl text-ink">Mi perfil</h1><p className="mt-2 text-sm text-muted">Consulta tu cuenta y actualiza tus datos de contacto.</p></header>
        {error && <p role="alert" className="mt-6 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">{error}</p>}
        {notice && <p role="status" className="mt-6 rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">{notice}</p>}
        {loading ? <p role="status" className="mt-8 text-sm text-muted">Cargando perfil…</p> : <form onSubmit={saveProfile} className="mt-8 space-y-5 rounded-2xl border border-line bg-white p-5 shadow-sm sm:p-7">
          <div><span className="block text-sm font-medium text-ink">Correo electrónico</span><p className="mt-1 rounded-lg bg-paper px-3 py-2.5 text-sm text-muted">{email}</p><p className="mt-1 text-xs text-muted">El correo se gestiona en los datos de cuenta.</p></div>
          <label className="block text-sm font-medium text-ink">Nombre<input className={inputClass} autoComplete="name" value={profile.name ?? ""} onChange={(event) => setProfile({ ...profile, name: event.target.value })} /></label>
          <label className="block text-sm font-medium text-ink">Teléfono<input className={inputClass} autoComplete="tel" type="tel" value={profile.phone ?? ""} onChange={(event) => setProfile({ ...profile, phone: event.target.value })} /></label>
          <label className="block text-sm font-medium text-ink">Dirección<input className={inputClass} autoComplete="street-address" value={profile.address ?? ""} onChange={(event) => setProfile({ ...profile, address: event.target.value })} /></label>
          <button type="submit" disabled={saving} className="rounded-lg bg-pine px-4 py-2.5 text-sm font-semibold text-white hover:bg-pine/90 disabled:cursor-wait disabled:opacity-60">{saving ? "Guardando…" : "Guardar cambios"}</button>
        </form>}
      </div>
    </main>
  </div>;
}
