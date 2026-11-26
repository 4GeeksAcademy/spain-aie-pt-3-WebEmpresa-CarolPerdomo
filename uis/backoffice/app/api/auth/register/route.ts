import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.API_URL ?? "http://127.0.0.1:8000";

export async function POST(request: NextRequest) {
  try {
    const { email, password } = await request.json();
    const response = await fetch(`${API_URL}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
      cache: "no-store",
    });
    const body = await response.json().catch(() => null);
    return NextResponse.json(body ?? { detail: "La API devolvió una respuesta no válida." }, { status: response.status });
  } catch {
    return NextResponse.json({ detail: "No se pudo conectar con FastAPI" }, { status: 503 });
  }
}
