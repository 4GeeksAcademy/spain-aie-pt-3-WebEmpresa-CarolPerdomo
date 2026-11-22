import { cookies } from "next/headers";
import { NextResponse } from "next/server";

const API_URL = process.env.API_URL ?? "http://127.0.0.1:8000";

export async function proxySupplierRequest(
  path: string,
  init: RequestInit = {},
) {
  const token = (await cookies()).get("access_token")?.value;

  if (!token) {
    return NextResponse.json({ detail: "Inicia sesión para continuar." }, { status: 401 });
  }

  try {
    const headers = new Headers(init.headers);
    headers.set("Authorization", `Bearer ${token}`);
    if (init.body) headers.set("Content-Type", "application/json");

    const response = await fetch(`${API_URL}${path}`, {
      ...init,
      headers,
      cache: "no-store",
    });

    if (response.status === 204) return new NextResponse(null, { status: 204 });

    const body = await response.text();
    return new NextResponse(body, {
      status: response.status,
      headers: { "Content-Type": response.headers.get("Content-Type") ?? "application/json" },
    });
  } catch {
    return NextResponse.json({ detail: "No se pudo conectar con el servidor." }, { status: 503 });
  }
}
