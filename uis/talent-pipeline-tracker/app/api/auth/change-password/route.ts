import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.API_URL ?? "http://127.0.0.1:8000";

export async function POST(request: NextRequest) {
  const authorization = request.headers.get("authorization");
  if (!authorization?.startsWith("Bearer ")) return NextResponse.json({ detail: "Missing or invalid token" }, { status: 401 });
  try {
    const response = await fetch(`${API_URL}/auth/change-password`, {
      method: "POST", headers: { Authorization: authorization, "Content-Type": "application/json" },
      body: await request.text(), cache: "no-store",
    });
    const body = await response.json().catch(() => null);
    return NextResponse.json(body ?? { detail: "Respuesta no válida de la API." }, { status: response.status });
  } catch {
    return NextResponse.json({ detail: "No se pudo conectar con la API." }, { status: 503 });
  }
}
