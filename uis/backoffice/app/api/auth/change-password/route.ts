import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.API_URL ?? "http://127.0.0.1:8000";

export async function POST(request: NextRequest) {
  const token = (await cookies()).get("access_token")?.value;
  if (!token) return NextResponse.json({ detail: "Inicia sesión para continuar." }, { status: 401 });

  try {
    const response = await fetch(`${API_URL}/auth/change-password`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify(await request.json()),
      cache: "no-store",
    });
    return NextResponse.json(await response.json(), { status: response.status });
  } catch {
    return NextResponse.json({ detail: "No se pudo conectar con el servidor." }, { status: 503 });
  }
}
