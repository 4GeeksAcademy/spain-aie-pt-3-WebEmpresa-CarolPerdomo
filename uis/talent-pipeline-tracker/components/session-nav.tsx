"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { clearAuthToken } from "@/lib/auth-client";

export function SessionNav() {
  const router = useRouter();
  return <nav className="session-nav" aria-label="Cuenta">
    <Link href="/account/profile">Mi perfil</Link>
    <button type="button" onClick={() => { clearAuthToken(); router.replace("/login"); }}>Cerrar sesión</button>
  </nav>;
}
