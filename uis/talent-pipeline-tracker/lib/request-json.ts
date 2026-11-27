import { NextResponse } from "next/server";

type JsonObjectResult =
  | { ok: true; value: Record<string, unknown> }
  | { ok: false; response: NextResponse };

export async function readJsonObject(request: Request): Promise<JsonObjectResult> {
  let value: unknown;
  try {
    value = await request.json();
  } catch {
    return {
      ok: false,
      response: NextResponse.json({ detail: "El cuerpo de la solicitud debe ser JSON válido." }, { status: 400 }),
    };
  }

  if (value === null || typeof value !== "object" || Array.isArray(value)) {
    return {
      ok: false,
      response: NextResponse.json({ detail: "El cuerpo de la solicitud debe ser un objeto JSON." }, { status: 400 }),
    };
  }

  return { ok: true, value: value as Record<string, unknown> };
}
