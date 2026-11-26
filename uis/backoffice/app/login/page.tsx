
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { saveAuthToken } from "@/lib/auth-client";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [notice, setNotice] = useState("");

  useEffect(() => {
    if (new URLSearchParams(window.location.search).get("reset") === "success") {
      const timer = window.setTimeout(() => setNotice("La contraseña se restableció. Ya puedes iniciar sesión."), 0);
      return () => window.clearTimeout(timer);
    }
  }, []);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(typeof data.detail === "string" ? data.detail : "Revisa el correo y la contraseña e inténtalo de nuevo.");
        return;
      }

      if (typeof data.access_token !== "string") {
        setError("La respuesta del servidor no incluyó un token de sesión.");
        return;
      }
      saveAuthToken(data.access_token);
      router.push("/");
      router.refresh();
    } catch {
      setError("No se pudo conectar con el servidor");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-100 px-4">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-md space-y-5 rounded-2xl bg-white p-8 shadow-lg"
      >
        <div>
          <h1 className="text-3xl font-bold text-slate-900">NEXOVA</h1>
          <p className="mt-2 text-sm text-slate-500">
            Acceso al Backoffice
          </p>
        </div>

        {notice && <p role="status" className="text-sm text-green-700">{notice}</p>}

        <div>
          <label htmlFor="email" className="mb-2 block text-sm font-medium">Correo electrónico</label>
          <input
            id="email"
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full rounded-lg border border-slate-300 p-3"
            placeholder="correo@empresa.com"
          />
        </div>

        <Link href="/forgot-password" className="block text-right text-sm text-slate-700 underline">
          ¿Olvidaste tu contraseña?
        </Link>

        <div>
          <label htmlFor="password" className="mb-2 block text-sm font-medium">Contraseña</label>
          <input
            id="password"
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded-lg border border-slate-300 p-3"
            placeholder="Tu contraseña"
          />
        </div>

        {error && (
          <p role="alert" className="text-sm text-red-600">{error}</p>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-lg bg-slate-900 p-3 font-semibold text-white hover:bg-slate-700 disabled:opacity-50"
        >
          {loading ? "Ingresando..." : "Iniciar sesión"}
        </button>
        <p className="text-center text-sm"><Link className="font-medium text-pine underline" href="/forgot-password">¿Olvidaste tu contraseña?</Link></p>
        <p className="text-center text-sm text-slate-600">¿Aún no tienes cuenta? <Link className="font-semibold text-slate-900 underline" href="/register">Crear cuenta</Link></p>
      </form>
    </main>
  );
}
