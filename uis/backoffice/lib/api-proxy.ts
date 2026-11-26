import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.API_URL ?? "http://127.0.0.1:8000";

export async function proxyApiRequest(request: NextRequest, path: string, method = request.method) {
  const authorization = request.headers.get("authorization");
  if (!authorization?.startsWith("Bearer ")) {
    return NextResponse.json({ detail: "Missing or invalid token" }, { status: 401 });
  }
  try {
    const body = method === "GET" || method === "HEAD" ? undefined : await request.text();
    const response = await fetch(`${API_URL}${path}`, {
      method,
      headers: { Authorization: authorization, ...(body ? { "Content-Type": "application/json" } : {}) },
      body,
      cache: "no-store",
    });
    const responseBody = response.status === 204 ? null : await response.json().catch(() => null);
    return responseBody === null
      ? new NextResponse(null, { status: response.status })
      : NextResponse.json(responseBody, { status: response.status });
  } catch {
    return NextResponse.json({ detail: "No se pudo conectar con FastAPI" }, { status: 503 });
  }
}
