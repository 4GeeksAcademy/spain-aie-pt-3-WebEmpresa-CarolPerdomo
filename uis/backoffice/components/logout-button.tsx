"use client";

import { clearAuthToken } from "@/lib/auth-client";
import { useRouter } from "next/navigation";

export function LogoutButton() {
  const router = useRouter();
  return <button
    type="button"
    onClick={() => { clearAuthToken(); router.replace("/login"); }}
    className="mt-4 text-xs font-semibold text-white/75 underline underline-offset-4 hover:text-white focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-leaf"
  >Cerrar sesión</button>;
}
