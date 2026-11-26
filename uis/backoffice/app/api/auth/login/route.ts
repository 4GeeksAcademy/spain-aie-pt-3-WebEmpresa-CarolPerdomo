
import { NextRequest, NextResponse } from "next/server";
import { readJsonObject } from "@/lib/request-json";

const API_URL = process.env.API_URL ?? "http://127.0.0.1:8000";

export async function POST(request: NextRequest) {
  const parsed = await readJsonObject(request);
  if (!parsed.ok) return parsed.response;

  try {
    const { email, password } = parsed.value;

    const response = await fetch(`${API_URL}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email, password }),
      cache: "no-store",
    });

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json(
        { detail: data.detail || "Credenciales incorrectas" },
        { status: response.status }
      );
    }

    return NextResponse.json({
      user: data.user,
      access_token: data.access_token,
      message: "Inicio de sesión correcto",
    });
  } catch {
    return NextResponse.json(
      { detail: "No se pudo conectar con FastAPI" },
      { status: 503 }
    );
  }
}
