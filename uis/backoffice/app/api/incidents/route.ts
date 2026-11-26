import { NextRequest } from "next/server";
import { proxyIncidentRequest } from "@/lib/incident-proxy";
import { readJsonObject } from "@/lib/request-json";

export function GET(request: NextRequest) {
  return proxyIncidentRequest(`/api/incidents${request.nextUrl.search}`, {}, request.headers.get("authorization"));
}

export async function POST(request: NextRequest) {
  const parsed = await readJsonObject(request);
  if (!parsed.ok) return parsed.response;
  return proxyIncidentRequest("/api/incidents", {
    method: "POST",
    body: JSON.stringify(parsed.value),
  }, request.headers.get("authorization"));
}
