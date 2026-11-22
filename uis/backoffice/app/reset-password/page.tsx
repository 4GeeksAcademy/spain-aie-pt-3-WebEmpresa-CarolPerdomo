"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function ResetPasswordPage() {
  const router = useRouter();
  const [token, setToken] = useState("");
  const [password, setPassword] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const timer = window.setTimeout(() => setToken(new URLSearchParams(window.location.search).get("token") ?? ""), 0);
    return () => window.clearTimeout(timer);
  }, []);

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    if (!token) { setError("El enlace no contiene un token válido."); return; }
    if (password !== confirmation) { setError("Las contraseñas no coinciden."); return; }
    setLoading(true);
    try {
      const response = await fetch("/api/auth/reset-password", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ token, new_password: password }) });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "El enlace no es válido o ha expirado.");
      router.push("/login?reset=success");
    } catch (cause) { setError(cause instanceof Error ? cause.message : "No se pudo conectar con el servidor."); }
    finally { setLoading(false); }
  }

  return <main className="flex min-h-screen items-center justify-center bg-slate-100 px-4"><form onSubmit={submit} className="w-full max-w-md space-y-5 rounded-2xl bg-white p-8 shadow-lg">
    <h1 className="text-2xl font-bold text-slate-900">Crear nueva contraseña</h1>
    <label className="block text-sm font-medium">Nueva contraseña<input type="password" required minLength={8} autoComplete="new-password" value={password} onChange={(event) => setPassword(event.target.value)} className="mt-2 w-full rounded-lg border border-slate-300 p-3" /></label>
    <label className="block text-sm font-medium">Confirmar contraseña<input type="password" required minLength={8} autoComplete="new-password" value={confirmation} onChange={(event) => setConfirmation(event.target.value)} className="mt-2 w-full rounded-lg border border-slate-300 p-3" /></label>
    {error && <p role="alert" className="text-sm text-red-600">{error} <Link className="underline" href="/forgot-password">Solicitar otro enlace</Link></p>}
    <button disabled={loading} className="w-full rounded-lg bg-slate-900 p-3 font-semibold text-white disabled:opacity-50">{loading ? "Guardando…" : "Guardar contraseña"}</button>
  </form></main>;
}
