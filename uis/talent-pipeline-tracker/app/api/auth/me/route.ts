import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.API_URL ?? "http://127.0.0.1:8000";

export async function GET(request: NextRequest) {
  const authorization = request.headers.get("authorization");
  if (!authorization?.startsWith("Bearer ")) return NextResponse.json({ detail: "Missing or invalid token" }, { status: 401 });
  try {
    const response = await fetch(`${API_URL}/auth/me`, { headers: { Authorization: authorization }, cache: "no-store" });
    return NextResponse.json(await response.json(), { status: response.status });
  } catch {
    return NextResponse.json({ detail: "No se pudo validar la sesión." }, { status: 503 });
  }
}
