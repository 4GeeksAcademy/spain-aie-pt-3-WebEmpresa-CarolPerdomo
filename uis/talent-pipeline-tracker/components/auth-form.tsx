"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import { apiFetch, saveAuthToken } from "@/lib/auth-client";

type Props = { mode: "login" | "register" };

export function AuthForm({ mode }: Props) {
  const router = useRouter();
  const [form, setForm] = useState({ email: "", password: "", name: "", phone: "", address: "" });
  const [error, setError] = useState("");
  const [fieldErrors, setFieldErrors] = useState<{ email?: string; password?: string }>({});
  const [busy, setBusy] = useState(false);
  const registering = mode === "register";

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setBusy(true); setError(""); setFieldErrors({});
    try {
      if (registering) {
        const response = await fetch("/api/auth/register", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email: form.email, password: form.password }) });
        const body = await response.json().catch(() => null);
        if (!response.ok) {
          if (Array.isArray(body?.detail)) {
            const nextErrors: { email?: string; password?: string } = {};
            for (const item of body.detail) {
              const field: unknown = Array.isArray(item?.loc) ? item.loc[item.loc.length - 1] : undefined;
              if ((field === "email" || field === "password") && typeof item?.msg === "string") {
                const key = field as "email" | "password";
                nextErrors[key] = key === "password" && item.msg.includes("at least 8") ? "La contraseña debe tener al menos 8 caracteres." : key === "email" ? "Ingresa un correo electrónico válido." : item.msg;
              }
            }
            setFieldErrors(nextErrors);
            if (!Object.keys(nextErrors).length) setError("Revisa los datos del formulario.");
          } else setError(typeof body?.detail === "string" ? body.detail : "No se pudo crear la cuenta. Revisa los datos.");
          return;
        }
      }

      const login = await fetch("/api/auth/login", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email: form.email, password: form.password }) });
      const session = await login.json().catch(() => null);
      if (!login.ok || typeof session?.access_token !== "string") throw new Error(registering ? "La cuenta se creó, pero no se pudo iniciar sesión. Usa el formulario de acceso." : (typeof session?.detail === "string" ? session.detail : "Correo o contraseña incorrectos."));
      saveAuthToken(session.access_token);

      if (registering) {
        const profile = Object.fromEntries(Object.entries({ name: form.name.trim(), phone: form.phone.trim(), address: form.address.trim() }).filter(([, value]) => value));
        if (Object.keys(profile).length) {
          const saved = await apiFetch("/api/profiles/me", { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(profile) });
          if (!saved.ok) throw new Error("La cuenta inició sesión, pero no se guardaron los datos de perfil. Puedes completarlos en Mi perfil.");
        }
      }
      router.replace("/"); router.refresh();
    } catch (cause) {
      const message = cause instanceof Error ? cause.message : "No se pudo completar la solicitud.";
      setError(message);
    } finally { setBusy(false); }
  }

  return <main className="shell auth-shell"><section className="panel auth-panel">
    <p className="eyebrow">NEXOVA / TALENT OPERATIONS</p>
    <h1>{registering ? "Crear cuenta" : "Iniciar sesión"}</h1>
    <p className="auth-description">{registering ? "Crea tu acceso y completa tus datos de perfil." : "Accede al pipeline de candidaturas."}</p>
    <form onSubmit={submit}>
      {registering && <div className="auth-fields">
        <label>Nombre (opcional)<input autoComplete="name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></label>
        <label>Teléfono (opcional)<input type="tel" autoComplete="tel" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} /></label>
        <label>Dirección (opcional)<input autoComplete="street-address" value={form.address} onChange={(e) => setForm({ ...form, address: e.target.value })} /></label>
      </div>}
      <div className="auth-fields">
        <label>Correo electrónico<input type="email" autoComplete="email" required aria-invalid={Boolean(fieldErrors.email)} aria-describedby={fieldErrors.email ? "register-email-error" : undefined} value={form.email} onChange={(e) => { setForm({ ...form, email: e.target.value }); setFieldErrors({ ...fieldErrors, email: undefined }); }} />{fieldErrors.email && <small id="register-email-error" className="form-error">{fieldErrors.email}</small>}</label>
        <label>Contraseña<input type="password" autoComplete={registering ? "new-password" : "current-password"} minLength={registering ? 8 : undefined} required aria-invalid={Boolean(fieldErrors.password)} aria-describedby={fieldErrors.password ? "register-password-error" : undefined} value={form.password} onChange={(e) => { setForm({ ...form, password: e.target.value }); setFieldErrors({ ...fieldErrors, password: undefined }); }} />{fieldErrors.password ? <small id="register-password-error" className="form-error">{fieldErrors.password}</small> : registering && <small>Mínimo 8 caracteres.</small>}</label>
      </div>
      {error && <p className="form-error" role="alert">{error} {error.includes("datos de perfil") && <Link href="/account/profile">Ir a Mi perfil</Link>}</p>}
      <div className="form-actions"><button className="button button-primary" disabled={busy}>{busy ? "Procesando…" : registering ? "Crear cuenta e iniciar sesión" : "Iniciar sesión"}</button></div>
    </form>
    <p className="auth-switch">{registering ? "¿Ya tienes cuenta? " : "¿Necesitas una cuenta? "}<Link href={registering ? "/login" : "/register"}>{registering ? "Inicia sesión" : "Regístrate"}</Link></p>
    {!registering && <p className="auth-switch"><Link href="/forgot-password">¿Olvidaste tu contraseña?</Link></p>}
  </section></main>;
}
