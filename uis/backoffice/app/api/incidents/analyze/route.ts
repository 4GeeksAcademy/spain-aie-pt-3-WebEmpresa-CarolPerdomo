import { forwardIncidentsRequest } from "@/lib/incidents-proxy";

export async function POST(request: Request) {
  return forwardIncidentsRequest(request, "/api/incidents/analyze");
}