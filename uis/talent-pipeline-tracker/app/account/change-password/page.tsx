import Link from "next/link";
import { ChangePasswordForm } from "@/components/password-flows";
import { SessionNav } from "@/components/session-nav";

export default function ChangePasswordPage() {
  return <main className="shell"><header className="topbar"><div><p className="eyebrow">NEXOVA / CUENTA</p><h1>Cambiar contraseña</h1></div><SessionNav /></header>
    <p className="back-link"><Link href="/account/profile">← Volver al perfil</Link></p><ChangePasswordForm />
  </main>;
}
