import { NextResponse } from "next/server";

const API_URL = process.env.API_URL ?? "http://127.0.0.1:8000";

export async function proxySupplierRequest(path: string, init: RequestInit = {}, authorization?: string | null) {
  if (!authorization?.startsWith("Bearer ")) {
    return NextResponse.json({ detail: "Missing or invalid token" }, { status: 401 });
  }
  try {
    const response = await fetch(`${API_URL}${path}`, {
      ...init,
      headers: { "Content-Type": "application/json", Authorization: authorization, ...init.headers },
      cache: "no-store",
    });
    const body = response.status === 204 ? null : await response.json().catch(() => null);
    return body === null
      ? new NextResponse(null, { status: response.status })
      : NextResponse.json(body, { status: response.status });
  } catch {
    return NextResponse.json({ detail: "No se pudo conectar con FastAPI" }, { status: 503 });
  }
}
