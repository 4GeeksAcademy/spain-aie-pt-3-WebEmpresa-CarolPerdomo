"use client";

import Link from "next/link";
import { useEffect, useState, type FormEvent } from "react";
import { apiFetch } from "@/lib/auth-client";
import { SessionNav } from "@/components/session-nav";

type User = { email: string };
type Profile = { name: string | null; phone: string | null; address: string | null };

export default function AccountProfilePage() {
  const [email, setEmail] = useState("");
  const [profile, setProfile] = useState<Profile>({ name: "", phone: "", address: "" });
  const [loading, setLoading] = useState(true); const [saving, setSaving] = useState(false); const [error, setError] = useState(""); const [notice, setNotice] = useState("");
  useEffect(() => {
    let active = true;
    void Promise.all([apiFetch("/api/users/me"), apiFetch("/api/profiles/me")]).then(async ([userResponse, profileResponse]) => {
      const [user, savedProfile] = await Promise.all([userResponse.json(), profileResponse.json()]) as [User, Profile];
      if (!userResponse.ok || !profileResponse.ok) throw new Error("No se pudo cargar la cuenta.");
      if (active) { setEmail(user.email); setProfile({ name: savedProfile.name ?? "", phone: savedProfile.phone ?? "", address: savedProfile.address ?? "" }); }
    }).catch((cause) => { if (active) setError(cause instanceof Error ? cause.message : "No se pudo cargar el perfil."); }).finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);

  async function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setSaving(true); setError(""); setNotice("");
    try {
      const response = await apiFetch("/api/profiles/me", { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(profile) });
      const body = await response.json().catch(() => null);
      if (!response.ok) throw new Error(typeof body?.detail === "string" ? body.detail : "No se pudo guardar el perfil.");
      setNotice("Perfil actualizado.");
    } catch (cause) { setError(cause instanceof Error ? cause.message : "No se pudo guardar el perfil."); }
    finally { setSaving(false); }
  }

  return <main className="shell"><header className="topbar"><div><p className="eyebrow">NEXOVA / CUENTA</p><h1>Mi perfil</h1></div><SessionNav /></header><p className="back-link"><Link href="/">← Volver al pipeline</Link></p>
    {error && <p role="alert" className="form-error">{error}</p>}{notice && <p role="status" className="feedback">{notice}</p>}
    {loading ? <div className="state" role="status">Cargando perfil…</div> : <section className="panel profile-panel"><div><p className="eyebrow">CUENTA</p><h2>Datos personales</h2></div><form onSubmit={save}>
      <label>Correo electrónico<input value={email} readOnly /></label>
      <label>Nombre<input autoComplete="name" value={profile.name ?? ""} onChange={(e) => setProfile({ ...profile, name: e.target.value })} /></label>
      <label>Teléfono<input type="tel" autoComplete="tel" value={profile.phone ?? ""} onChange={(e) => setProfile({ ...profile, phone: e.target.value })} /></label>
      <label>Dirección<input autoComplete="street-address" value={profile.address ?? ""} onChange={(e) => setProfile({ ...profile, address: e.target.value })} /></label>
      <div className="form-actions"><button className="button button-primary" disabled={saving}>{saving ? "Guardando…" : "Guardar cambios"}</button></div>
    </form></section>}
  </main>;
}
