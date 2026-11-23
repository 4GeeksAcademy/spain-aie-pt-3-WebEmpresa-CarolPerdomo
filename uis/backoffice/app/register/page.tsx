"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import { apiFetch, saveAuthToken } from "@/lib/auth-client";

type ApiError = { detail?: unknown };

function messageFrom(body: ApiError | null, fallback: string) {
  if (typeof body?.detail === "string") return body.detail;
  if (Array.isArray(body?.detail)) {
    return body.detail.map((item) => typeof item === "object" && item && "msg" in item ? String(item.msg) : "").filter(Boolean).join(" ") || fallback;
  }
  return fallback;
}

export default function RegisterPage() {
  const router = useRouter();
  const [form, setForm] = useState({ name: "", email: "", password: "", phone: "", address: "" });
  const [error, setError] = useState("");
  const [fieldErrors, setFieldErrors] = useState<{ email?: string; password?: string }>({});
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setFieldErrors({});
    setLoading(true);
    try {
      const registration = await fetch("/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: form.email, password: form.password }),
      });
      const registrationBody = await registration.json().catch(() => null);
      if (!registration.ok) {
        if (Array.isArray(registrationBody?.detail)) {
          const nextFieldErrors: { email?: string; password?: string } = {};
          for (const item of registrationBody.detail) {
            const field: unknown = Array.isArray(item?.loc) ? item.loc[item.loc.length - 1] : undefined;
            if ((field === "email" || field === "password") && typeof item?.msg === "string") {
              const key = field as "email" | "password";
              nextFieldErrors[key] = key === "password" && item.msg.includes("at least 8") ? "La contraseña debe tener al menos 8 caracteres." : key === "email" ? "Ingresa un correo electrónico válido." : item.msg;
            }
          }
          setFieldErrors(nextFieldErrors);
          if (!Object.keys(nextFieldErrors).length) setError(messageFrom(registrationBody, "No se pudo crear la cuenta."));
        } else setError(messageFrom(registrationBody, "No se pudo crear la cuenta. Revisa los datos e inténtalo de nuevo."));
        return;
      }

      const login = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: form.email, password: form.password }),
      });
      const loginBody = await login.json().catch(() => null);
      if (!login.ok || typeof loginBody?.access_token !== "string") {
        setError("La cuenta se creó, pero no pudimos iniciar sesión. Ve al login para entrar.");
        return;
      }
      saveAuthToken(loginBody.access_token);

      const profile = { name: form.name.trim(), phone: form.phone.trim(), address: form.address.trim() };
      if (Object.values(profile).some(Boolean)) {
        const profileResponse = await apiFetch("/api/profiles/me", {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(Object.fromEntries(Object.entries(profile).filter(([, value]) => value))),
        });
        if (!profileResponse.ok) {
          setError("La cuenta está creada e iniciada. No se pudo guardar el perfil; puedes completarlo desde Mi perfil.");
          return;
        }
      }

      router.replace("/");
      router.refresh();
    } catch {
      setError("No se pudo conectar con el servidor. Comprueba que la API esté disponible.");
    } finally {
      setLoading(false);
    }
  }

  const inputClass = "mt-1 w-full rounded-lg border border-slate-300 bg-white p-3 text-sm outline-none focus:border-slate-700 focus:ring-2 focus:ring-slate-900/10";

  return <main className="flex min-h-screen items-center justify-center bg-slate-100 px-4 py-10">
    <form onSubmit={handleSubmit} className="w-full max-w-xl space-y-5 rounded-2xl bg-white p-6 shadow-lg sm:p-8">
      <header><p className="text-sm font-semibold uppercase tracking-widest text-slate-500">Nexova · Backoffice</p><h1 className="mt-2 text-3xl font-bold text-slate-900">Crear cuenta</h1><p className="mt-2 text-sm text-slate-600">Registra tus credenciales y los datos básicos de tu perfil.</p></header>
      <div className="grid gap-4 sm:grid-cols-2">
        <label htmlFor="name" className="text-sm font-medium text-slate-800">Nombre <span className="font-normal text-slate-500">(opcional)</span><input id="name" autoComplete="name" value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} className={inputClass} /></label>
        <label htmlFor="email" className="text-sm font-medium text-slate-800">Correo electrónico<input id="email" type="email" autoComplete="email" required aria-invalid={Boolean(fieldErrors.email)} aria-describedby={fieldErrors.email ? "email-error" : undefined} value={form.email} onChange={(event) => { setForm({ ...form, email: event.target.value }); setFieldErrors({ ...fieldErrors, email: undefined }); }} className={inputClass} />{fieldErrors.email && <span id="email-error" className="mt-1 text-xs text-red-700">{fieldErrors.email}</span>}</label>
        <label htmlFor="password" className="text-sm font-medium text-slate-800 sm:col-span-2">Contraseña<input id="password" type="password" autoComplete="new-password" minLength={8} required aria-invalid={Boolean(fieldErrors.password)} aria-describedby={fieldErrors.password ? "password-error" : undefined} value={form.password} onChange={(event) => { setForm({ ...form, password: event.target.value }); setFieldErrors({ ...fieldErrors, password: undefined }); }} className={inputClass} />{fieldErrors.password ? <span id="password-error" className="mt-1 text-xs text-red-700">{fieldErrors.password}</span> : <span className="mt-1 block text-xs text-slate-500">Mínimo 8 caracteres.</span>}</label>
        <label htmlFor="phone" className="text-sm font-medium text-slate-800">Teléfono <span className="font-normal text-slate-500">(opcional)</span><input id="phone" type="tel" autoComplete="tel" value={form.phone} onChange={(event) => setForm({ ...form, phone: event.target.value })} className={inputClass} /></label>
        <label htmlFor="address" className="text-sm font-medium text-slate-800">Dirección <span className="font-normal text-slate-500">(opcional)</span><input id="address" autoComplete="street-address" value={form.address} onChange={(event) => setForm({ ...form, address: event.target.value })} className={inputClass} /></label>
      </div>
      {error && <p role="alert" className="rounded-lg bg-red-50 p-3 text-sm text-red-800">{error} {error.startsWith("La cuenta está creada") && <Link className="font-semibold underline" href="/account/profile">Abrir Mi perfil</Link>}</p>}
      <button type="submit" disabled={loading} className="w-full rounded-lg bg-slate-900 p-3 font-semibold text-white hover:bg-slate-700 disabled:cursor-wait disabled:opacity-60">{loading ? "Creando cuenta…" : "Crear cuenta e iniciar sesión"}</button>
      <p className="text-center text-sm text-slate-600">¿Ya tienes cuenta? <Link className="font-semibold text-slate-900 underline" href="/login">Iniciar sesión</Link></p>
    </form>
  </main>;
}
