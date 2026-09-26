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
  title: "Nexova Solutions | Talento que impulsa empresas",
  description:
    "Headhunting, outsourcing de atención al cliente y formación corporativa para empresas de tecnología, retail y servicios financieros.",
  metadataBase: new URL("https://nexova.com"),
  alternates: {
    canonical: "/",
  },
  openGraph: {
    title: "Nexova Solutions | Talento que impulsa empresas",
    description:
      "Conectamos empresas en crecimiento con el talento y los equipos que necesitan.",
    url: "https://nexova.com",
    siteName: "Nexova Solutions",
    locale: "es_ES",
    type: "website",
  },
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="es" className={`${dmSans.variable} ${dmSerif.variable} h-full antialiased`}>
      <body className="min-h-full bg-paper font-sans text-ink">{children}</body>
    </html>
  );
}
