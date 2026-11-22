"use client";

import { useState } from "react";
import Link from "next/link";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      const response = await fetch("/api/auth/forgot-password", {
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email }),
      });
      if (!response.ok) throw new Error("No se pudo enviar la solicitud. Inténtalo de nuevo.");
      setSent(true);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "No se pudo conectar con el servidor.");
    } finally { setLoading(false); }
  }

  return <main className="flex min-h-screen items-center justify-center bg-slate-100 px-4"><form onSubmit={submit} className="w-full max-w-md space-y-5 rounded-2xl bg-white p-8 shadow-lg">
    <h1 className="text-2xl font-bold text-slate-900">¿Olvidaste tu contraseña?</h1>
    {sent ? <p role="status" className="text-sm text-slate-700">Si esa dirección está registrada, recibirás un enlace en breve.</p> : <>
      <p className="text-sm text-slate-600">Escribe el correo asociado a tu cuenta.</p>
      <label className="block text-sm font-medium">Correo electrónico<input type="email" required autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} className="mt-2 w-full rounded-lg border border-slate-300 p-3" /></label>
      {error && <p role="alert" className="text-sm text-red-600">{error}</p>}
      <button disabled={loading} className="w-full rounded-lg bg-slate-900 p-3 font-semibold text-white disabled:opacity-50">{loading ? "Enviando…" : "Enviar enlace"}</button>
    </>}
    <Link className="block text-sm text-slate-700 underline" href="/login">Volver al inicio de sesión</Link>
  </form></main>;
}
