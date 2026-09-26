import type { Metadata } from "next";
import { DM_Sans, DM_Serif_Display } from "next/font/google";
import "./globals.css";

const dmSans = DM_Sans({
  variable: "--font-dm-sans",
  subsets: ["latin"],
});

const dmSerif = DM_Serif_Display({
  variable: "--font-dm-serif",
  subsets: ["latin"],
  weight: "400",
});

export const metadata: Metadata = {
  title: "Panel ejecutivo | Nexova",
  description: "Vista interna de las operaciones y prioridades de Nexova.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="es" className={`${dmSans.variable} ${dmSerif.variable} h-full antialiased`}>
      <body className="min-h-full bg-paper font-sans text-ink">{children}</body>
    </html>
  );
}
