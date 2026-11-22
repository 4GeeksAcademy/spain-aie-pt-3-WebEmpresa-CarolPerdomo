"use client";

import { useState } from "react";
import Link from "next/link";

export default function ChangePasswordPage() {
  const [current, setCurrent] = useState("");
  const [password, setPassword] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError(""); setMessage("");
    if (password !== confirmation) { setError("Las contraseñas nuevas no coinciden."); return; }
    setLoading(true);
    try {
      const response = await fetch("/api/auth/change-password", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ current_password: current, new_password: password }) });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "No se pudo cambiar la contraseña.");
      setMessage("La contraseña se actualizó correctamente."); setCurrent(""); setPassword(""); setConfirmation("");
    } catch (cause) { setError(cause instanceof Error ? cause.message : "No se pudo conectar con el servidor."); }
    finally { setLoading(false); }
  }

  return <main className="mx-auto min-h-screen max-w-xl px-4 py-12"><form onSubmit={submit} className="space-y-5 rounded-2xl bg-white p-8 shadow-lg">
    <h1 className="text-2xl font-bold text-slate-900">Cambiar contraseña</h1>
    <label className="block text-sm font-medium">Contraseña actual<input type="password" required autoComplete="current-password" value={current} onChange={(event) => setCurrent(event.target.value)} className="mt-2 w-full rounded-lg border border-slate-300 p-3" /></label>
    <label className="block text-sm font-medium">Nueva contraseña<input type="password" required minLength={8} autoComplete="new-password" value={password} onChange={(event) => setPassword(event.target.value)} className="mt-2 w-full rounded-lg border border-slate-300 p-3" /></label>
    <label className="block text-sm font-medium">Confirmar nueva contraseña<input type="password" required minLength={8} autoComplete="new-password" value={confirmation} onChange={(event) => setConfirmation(event.target.value)} className="mt-2 w-full rounded-lg border border-slate-300 p-3" /></label>
    {error && <p role="alert" className="text-sm text-red-600">{error}</p>}{message && <p role="status" className="text-sm text-green-700">{message}</p>}
    <button disabled={loading} className="w-full rounded-lg bg-slate-900 p-3 font-semibold text-white disabled:opacity-50">{loading ? "Guardando…" : "Actualizar contraseña"}</button>
    <Link href="/" className="block text-sm text-slate-700 underline">Volver al panel</Link>
  </form></main>;
}
