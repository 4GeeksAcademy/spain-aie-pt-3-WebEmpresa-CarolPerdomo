import Link from "next/link";
import { Sidebar } from "@/components/sidebar";
import { ChangePasswordForm } from "@/components/password-flows";

export default function ChangePasswordPage() {
  return <div className="min-h-screen lg:grid lg:grid-cols-[248px_minmax(0,1fr)]"><Sidebar /><main className="min-w-0 px-4 py-8 sm:px-7 lg:px-10 lg:py-10"><div className="mx-auto max-w-3xl">
    <Link href="/account/profile" className="text-sm font-semibold text-pine hover:underline">← Volver al perfil</Link>
    <header className="mt-7 border-b border-line pb-6"><p className="text-xs font-bold uppercase tracking-[0.18em] text-muted">Cuenta</p><h1 className="mt-2 font-display text-4xl text-ink">Cambiar contraseña</h1></header>
    <ChangePasswordForm />
  </div></main></div>;
}
