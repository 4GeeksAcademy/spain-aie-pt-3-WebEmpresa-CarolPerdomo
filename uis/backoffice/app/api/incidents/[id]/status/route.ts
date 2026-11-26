import { NextRequest } from "next/server";
import { proxyIncidentRequest } from "@/lib/incident-proxy";

type RouteContext = { params: Promise<{ id: string }> };

export async function PATCH(request: NextRequest, { params }: RouteContext) {
  const { id } = await params;
  return proxyIncidentRequest(`/api/incidents/${encodeURIComponent(id)}/status`, {
    method: "PATCH",
    body: JSON.stringify(await request.json()),
  }, request.headers.get("authorization"));
}
