
import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.API_URL ?? "http://127.0.0.1:8000";

export async function POST(request: NextRequest) {
  try {
    const { email, password } = await request.json();

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

    const result = NextResponse.json({
      user: data.user,
      message: "Inicio de sesión correcto",
    });

    result.cookies.set("access_token", data.access_token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      path: "/",
      maxAge: 60 * 60 * 24,
    });

    return result;
  } catch {
    return NextResponse.json(
      { detail: "No se pudo conectar con FastAPI" },
      { status: 503 }
    );
  }
}
