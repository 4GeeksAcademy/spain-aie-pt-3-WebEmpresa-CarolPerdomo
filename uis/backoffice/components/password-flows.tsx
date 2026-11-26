"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import { apiFetch } from "@/lib/auth-client";

function messageFrom(body: { detail?: unknown } | null, fallback: string) {
  return typeof body?.detail === "string" ? body.detail : fallback;
}

export function ForgotPasswordForm() {
  const [email, setEmail] = useState("");
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setBusy(true); setNotice(""); setError("");
    try {
      const response = await fetch("/api/auth/forgot-password", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email }) });
      if (!response.ok) throw new Error("No se pudo procesar la solicitud. Inténtalo de nuevo más tarde.");
      setNotice("Si el correo está registrado, recibirás un enlace para restablecer la contraseña.");
    } catch (cause) { setError(cause instanceof Error ? cause.message : "No se pudo procesar la solicitud."); }
    finally { setBusy(false); }
  }
  return <main className="flex min-h-screen items-center justify-center bg-slate-100 px-4"><section className="w-full max-w-md space-y-5 rounded-2xl bg-white p-8 shadow-lg">
    <h1 className="text-3xl font-bold text-slate-900">Restablecer contraseña</h1><p className="text-sm text-slate-600">Escribe el correo asociado a tu cuenta.</p>
    <form onSubmit={submit} className="space-y-4"><label htmlFor="reset-email" className="block text-sm font-medium">Correo electrónico<input id="reset-email" className="mt-2 w-full rounded-lg border border-slate-300 p-3" type="email" autoComplete="email" required value={email} onChange={(event) => setEmail(event.target.value)} /></label>
      {error && <p role="alert" className="text-sm text-red-700">{error}</p>}{notice && <p role="status" className="text-sm text-emerald-800">{notice}</p>}
      <button disabled={busy} className="w-full rounded-lg bg-slate-900 p-3 font-semibold text-white disabled:opacity-50">{busy ? "Enviando…" : "Enviar enlace"}</button>
    </form><Link className="block text-center text-sm font-semibold text-pine underline" href="/login">Volver al inicio de sesión</Link>
  </section></main>;
}

export function ResetPasswordForm({ token }: { token: string }) {
  const router = useRouter();
  const [password, setPassword] = useState(""); const [confirmation, setConfirmation] = useState("");
  const [busy, setBusy] = useState(false); const [error, setError] = useState(""); const [success, setSuccess] = useState(false);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError("");
    if (password !== confirmation) { setError("Las contraseñas no coinciden."); return; }
    setBusy(true);
    try {
      const response = await fetch("/api/auth/reset-password", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ token, new_password: password }) });
      const body = await response.json().catch(() => null);
      if (!response.ok) throw new Error(messageFrom(body, "El enlace no es válido o ha caducado."));
      setSuccess(true); window.setTimeout(() => router.replace("/login"), 1200);
    } catch (cause) { setError(cause instanceof Error ? cause.message : "No se pudo cambiar la contraseña."); }
    finally { setBusy(false); }
  }
  return <main className="flex min-h-screen items-center justify-center bg-slate-100 px-4"><section className="w-full max-w-md space-y-5 rounded-2xl bg-white p-8 shadow-lg">
    <h1 className="text-3xl font-bold text-slate-900">Nueva contraseña</h1>
    {!token ? <p role="alert" className="text-sm text-red-700">Falta el enlace de restablecimiento o no es válido.</p> : <form onSubmit={submit} className="space-y-4">
      <label className="block text-sm font-medium">Nueva contraseña<input className="mt-2 w-full rounded-lg border border-slate-300 p-3" type="password" autoComplete="new-password" minLength={8} required value={password} onChange={(event) => setPassword(event.target.value)} /></label>
      <label className="block text-sm font-medium">Confirmar contraseña<input className="mt-2 w-full rounded-lg border border-slate-300 p-3" type="password" autoComplete="new-password" minLength={8} required value={confirmation} onChange={(event) => setConfirmation(event.target.value)} /></label>
      {error && <div role="alert" className="text-sm text-red-700">{error} <Link className="font-semibold underline" href="/forgot-password">Solicitar otro enlace</Link></div>}
      {success && <p role="status" className="text-sm text-emerald-800">Contraseña actualizada. Redirigiendo al inicio de sesión…</p>}
      <button disabled={busy || success} className="w-full rounded-lg bg-slate-900 p-3 font-semibold text-white disabled:opacity-50">{busy ? "Guardando…" : "Guardar contraseña"}</button>
    </form>}
    <Link className="block text-center text-sm font-semibold text-pine underline" href="/forgot-password">Solicitar otro enlace</Link>
  </section></main>;
}

export function ChangePasswordForm() {
  const [currentPassword, setCurrentPassword] = useState(""); const [password, setPassword] = useState(""); const [confirmation, setConfirmation] = useState("");
  const [busy, setBusy] = useState(false); const [error, setError] = useState(""); const [notice, setNotice] = useState("");
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError(""); setNotice("");
    if (password !== confirmation) { setError("Las contraseñas nuevas no coinciden."); return; }
    setBusy(true);
    try {
      const response = await apiFetch("/api/auth/change-password", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ current_password: currentPassword, new_password: password }) });
      const body = await response.json().catch(() => null);
      if (!response.ok) throw new Error(messageFrom(body, "No se pudo cambiar la contraseña."));
      setCurrentPassword(""); setPassword(""); setConfirmation(""); setNotice("Contraseña cambiada correctamente.");
    } catch (cause) { setError(cause instanceof Error ? cause.message : "No se pudo cambiar la contraseña."); }
    finally { setBusy(false); }
  }
  return <form onSubmit={submit} className="mt-8 space-y-5 rounded-2xl border border-line bg-white p-5 shadow-sm sm:p-7">
    <label className="block text-sm font-medium text-ink">Contraseña actual<input className="mt-1 w-full rounded-lg border border-line p-3" type="password" autoComplete="current-password" required value={currentPassword} onChange={(event) => setCurrentPassword(event.target.value)} /></label>
    <label className="block text-sm font-medium text-ink">Nueva contraseña<input className="mt-1 w-full rounded-lg border border-line p-3" type="password" autoComplete="new-password" minLength={8} required value={password} onChange={(event) => setPassword(event.target.value)} /><span className="text-xs text-muted">Mínimo 8 caracteres.</span></label>
    <label className="block text-sm font-medium text-ink">Confirmar nueva contraseña<input className="mt-1 w-full rounded-lg border border-line p-3" type="password" autoComplete="new-password" minLength={8} required value={confirmation} onChange={(event) => setConfirmation(event.target.value)} /></label>
    {error && <p role="alert" className="text-sm text-red-700">{error}</p>}{notice && <p role="status" className="text-sm text-emerald-800">{notice}</p>}
    <button disabled={busy} className="rounded-lg bg-pine px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-50">{busy ? "Guardando…" : "Cambiar contraseña"}</button>
  </form>;
}
