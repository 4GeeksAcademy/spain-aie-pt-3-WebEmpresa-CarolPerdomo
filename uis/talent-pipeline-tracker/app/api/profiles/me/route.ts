import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.API_URL ?? "http://127.0.0.1:8000";

async function forward(request: NextRequest, method: "GET" | "PUT") {
  const authorization = request.headers.get("authorization");
  if (!authorization?.startsWith("Bearer ")) return NextResponse.json({ detail: "Missing or invalid token" }, { status: 401 });
  try {
    const body = method === "PUT" ? await request.text() : undefined;
    const response = await fetch(`${API_URL}/profiles/me`, {
      method, headers: { Authorization: authorization, ...(body ? { "Content-Type": "application/json" } : {}) }, body, cache: "no-store",
    });
    return NextResponse.json(await response.json(), { status: response.status });
  } catch {
    return NextResponse.json({ detail: "No se pudo conectar con la API." }, { status: 503 });
  }
}

export function GET(request: NextRequest) { return forward(request, "GET"); }
export function PUT(request: NextRequest) { return forward(request, "PUT"); }
