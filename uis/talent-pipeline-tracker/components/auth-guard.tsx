"use client";

import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState, type ReactNode } from "react";
import { apiFetch, getAuthToken } from "@/lib/auth-client";

const publicPaths = new Set(["/login", "/register", "/forgot-password", "/reset-password"]);

export function AuthGuard({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const isPublic = publicPaths.has(pathname);
  const [verification, setVerification] = useState<{ path: string; error?: string } | null>(null);

  useEffect(() => {
    if (isPublic) return;
    let active = true;
    const onUnauthorized = () => router.replace("/login");
    window.addEventListener("nexova:unauthorized", onUnauthorized);
    if (!getAuthToken()) {
      router.replace("/login");
    } else {
      void apiFetch("/api/users/me").then((response) => {
        if (active && response.ok) setVerification({ path: pathname });
        else if (active && response.status !== 401) setVerification({ path: pathname, error: "No se pudo validar la sesión. Inténtalo de nuevo." });
      }).catch(() => {
        if (active) setVerification({ path: pathname, error: "No se pudo conectar con el servicio de autenticación." });
      });
    }
    return () => { active = false; window.removeEventListener("nexova:unauthorized", onUnauthorized); };
  }, [isPublic, pathname, router]);

  if (isPublic) return <>{children}</>;
  if (verification?.path !== pathname) return <main className="shell"><div className="state" role="status">Verificando sesión…</div></main>;
  if (verification.error) return <main className="shell"><div className="state state-error" role="alert">{verification.error}</div></main>;
  return <>{children}</>;
}
