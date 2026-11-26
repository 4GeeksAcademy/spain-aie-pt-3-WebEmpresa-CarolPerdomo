import { NextRequest } from "next/server";
import { proxyIncidentRequest } from "@/lib/incident-proxy";

type RouteContext = { params: Promise<{ id: string }> };

export async function GET(request: NextRequest, { params }: RouteContext) {
  const { id } = await params;
  return proxyIncidentRequest(`/api/incidents/${encodeURIComponent(id)}`, {}, request.headers.get("authorization"));
}
