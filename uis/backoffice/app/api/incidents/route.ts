import { NextRequest } from "next/server";
import { proxyIncidentRequest } from "@/lib/incident-proxy";

export function GET(request: NextRequest) {
  return proxyIncidentRequest(`/api/incidents${request.nextUrl.search}`, {}, request.headers.get("authorization"));
}

export async function POST(request: NextRequest) {
  return proxyIncidentRequest("/api/incidents", {
    method: "POST",
    body: JSON.stringify(await request.json()),
  }, request.headers.get("authorization"));
}
