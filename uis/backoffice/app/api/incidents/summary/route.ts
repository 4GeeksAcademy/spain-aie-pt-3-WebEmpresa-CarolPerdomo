import { NextRequest } from "next/server";
import { proxyIncidentRequest } from "@/lib/incident-proxy";

export function GET(request: NextRequest) {
  return proxyIncidentRequest("/api/incidents/summary", {}, request.headers.get("authorization"));
}
