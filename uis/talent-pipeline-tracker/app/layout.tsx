import type { Metadata } from "next";
import "./globals.css";
import { AuthGuard } from "@/components/auth-guard";

export const metadata: Metadata = {
  title: "Talent Pipeline | Nexova",
  description: "Gestión de candidaturas de Nexova",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return <html lang="es"><body><AuthGuard>{children}</AuthGuard></body></html>;
}
