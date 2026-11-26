import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.API_URL ?? "http://127.0.0.1:8000";
const TRACKER_API_URL = process.env.TRACKER_API_URL ?? "https://playground.4geeks.com/tracker/api/v1";
type RouteContext = { params: Promise<{ path: string[] }> };

async function forward(request: NextRequest, context: RouteContext) {
  const authorization = request.headers.get("authorization");
  if (!authorization?.startsWith("Bearer ")) return NextResponse.json({ detail: "Missing or invalid token" }, { status: 401 });
  try {
    const session = await fetch(`${API_URL}/users/me`, { headers: { Authorization: authorization }, cache: "no-store" });
    if (session.status === 401) return NextResponse.json({ detail: "Invalid or expired token" }, { status: 401 });
    if (!session.ok) return NextResponse.json({ detail: "No se pudo validar la sesión." }, { status: 503 });

    const { path } = await context.params;
    const safePath = path.map((part) => encodeURIComponent(part)).join("/");
    const body = ["GET", "HEAD"].includes(request.method) ? undefined : await request.text();
    const response = await fetch(`${TRACKER_API_URL}/${safePath}${request.nextUrl.search}`, {
      method: request.method,
      headers: body ? { "Content-Type": request.headers.get("content-type") ?? "application/json" } : undefined,
      body,
      cache: "no-store",
    });
    const responseBody = await response.text();
    return new NextResponse(responseBody || null, {
      status: response.status,
      headers: { "Content-Type": response.headers.get("content-type") ?? "application/json" },
    });
  } catch {
    return NextResponse.json({ detail: "No se pudo conectar con el servicio de candidaturas." }, { status: 503 });
  }
}

export const GET = forward;
export const POST = forward;
export const PUT = forward;
export const PATCH = forward;
export const DELETE = forward;
