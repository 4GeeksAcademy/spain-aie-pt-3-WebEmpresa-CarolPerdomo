"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import { apiFetch } from "@/lib/auth-client";

function detail(body: { detail?: unknown } | null, fallback: string) {
  return typeof body?.detail === "string" ? body.detail : fallback;
}

export function ForgotPasswordForm() {
  const [email, setEmail] = useState(""); const [busy, setBusy] = useState(false); const [notice, setNotice] = useState(""); const [error, setError] = useState("");
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setBusy(true); setError(""); setNotice("");
    try {
      const response = await fetch("/api/auth/forgot-password", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email }) });
      if (!response.ok) throw new Error("No se pudo procesar la solicitud. Inténtalo de nuevo más tarde.");
      setNotice("Si el correo está registrado, recibirás un enlace para restablecer la contraseña.");
    } catch (cause) { setError(cause instanceof Error ? cause.message : "No se pudo procesar la solicitud."); }
    finally { setBusy(false); }
  }
  return <main className="shell auth-shell"><section className="panel auth-panel"><p className="eyebrow">NEXOVA / ACCESO</p><h1>Restablecer contraseña</h1><p className="auth-description">Escribe el correo asociado a tu cuenta.</p>
    <form onSubmit={submit} className="auth-fields"><label>Correo electrónico<input type="email" autoComplete="email" required value={email} onChange={(event) => setEmail(event.target.value)} /></label>
      {error && <p className="form-error" role="alert">{error}</p>}{notice && <p role="status" className="feedback">{notice}</p>}
      <div className="form-actions"><button className="button button-primary" disabled={busy}>{busy ? "Enviando…" : "Enviar enlace"}</button></div>
    </form><p className="auth-switch"><Link href="/login">Volver al inicio de sesión</Link></p>
  </section></main>;
}

export function ResetPasswordForm({ token }: { token: string }) {
  const router = useRouter(); const [password, setPassword] = useState(""); const [confirmation, setConfirmation] = useState("");
  const [busy, setBusy] = useState(false); const [error, setError] = useState(""); const [success, setSuccess] = useState(false);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError(""); if (password !== confirmation) { setError("Las contraseñas no coinciden."); return; }
    setBusy(true);
    try {
      const response = await fetch("/api/auth/reset-password", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ token, new_password: password }) });
      const body = await response.json().catch(() => null);
      if (!response.ok) throw new Error(detail(body, "El enlace no es válido o ha caducado."));
      setSuccess(true); window.setTimeout(() => router.replace("/login"), 1200);
    } catch (cause) { setError(cause instanceof Error ? cause.message : "No se pudo cambiar la contraseña."); }
    finally { setBusy(false); }
  }
  return <main className="shell auth-shell"><section className="panel auth-panel"><p className="eyebrow">NEXOVA / ACCESO</p><h1>Nueva contraseña</h1>
    {!token ? <p role="alert" className="form-error">Falta el enlace de restablecimiento o no es válido.</p> : <form onSubmit={submit} className="auth-fields">
      <label>Nueva contraseña<input type="password" autoComplete="new-password" minLength={8} required value={password} onChange={(event) => setPassword(event.target.value)} /><small>Mínimo 8 caracteres.</small></label>
      <label>Confirmar contraseña<input type="password" autoComplete="new-password" minLength={8} required value={confirmation} onChange={(event) => setConfirmation(event.target.value)} /></label>
      {error && <p role="alert" className="form-error">{error} <Link href="/forgot-password">Solicitar otro enlace</Link></p>}{success && <p role="status" className="feedback">Contraseña actualizada. Redirigiendo al inicio de sesión…</p>}
      <div className="form-actions"><button className="button button-primary" disabled={busy || success}>{busy ? "Guardando…" : "Guardar contraseña"}</button></div>
    </form>}
    <p className="auth-switch"><Link href="/forgot-password">Solicitar otro enlace</Link></p>
  </section></main>;
}

export function ChangePasswordForm() {
  const [currentPassword, setCurrentPassword] = useState(""); const [password, setPassword] = useState(""); const [confirmation, setConfirmation] = useState("");
  const [busy, setBusy] = useState(false); const [error, setError] = useState(""); const [notice, setNotice] = useState("");
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError(""); setNotice(""); if (password !== confirmation) { setError("Las contraseñas nuevas no coinciden."); return; }
    setBusy(true);
    try {
      const response = await apiFetch("/api/auth/change-password", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ current_password: currentPassword, new_password: password }) });
      const body = await response.json().catch(() => null);
      if (!response.ok) throw new Error(detail(body, "No se pudo cambiar la contraseña."));
      setCurrentPassword(""); setPassword(""); setConfirmation(""); setNotice("Contraseña cambiada correctamente.");
    } catch (cause) { setError(cause instanceof Error ? cause.message : "No se pudo cambiar la contraseña."); }
    finally { setBusy(false); }
  }
  return <section className="panel profile-panel"><form onSubmit={submit}>
    <label>Contraseña actual<input type="password" autoComplete="current-password" required value={currentPassword} onChange={(event) => setCurrentPassword(event.target.value)} /></label>
    <label>Nueva contraseña<input type="password" autoComplete="new-password" minLength={8} required value={password} onChange={(event) => setPassword(event.target.value)} /><small>Mínimo 8 caracteres.</small></label>
    <label>Confirmar nueva contraseña<input type="password" autoComplete="new-password" minLength={8} required value={confirmation} onChange={(event) => setConfirmation(event.target.value)} /></label>
    {error && <p className="form-error" role="alert">{error}</p>}{notice && <p className="feedback" role="status">{notice}</p>}
    <div className="form-actions"><button className="button button-primary" disabled={busy}>{busy ? "Guardando…" : "Cambiar contraseña"}</button></div>
  </form></section>;
}
