import { NextRequest, NextResponse } from "next/server";
import { readJsonObject } from "@/lib/request-json";

const API_URL = process.env.API_URL ?? "http://127.0.0.1:8000";

export async function POST(request: NextRequest) {
  const parsed = await readJsonObject(request);
  if (!parsed.ok) return parsed.response;

  try {
    const response = await fetch(`${API_URL}/auth/login`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: parsed.value.email, password: parsed.value.password }), cache: "no-store",
    });
    return NextResponse.json(await response.json(), { status: response.status });
  } catch {
    return NextResponse.json({ detail: "No se pudo conectar con la API." }, { status: 503 });
  }
}
