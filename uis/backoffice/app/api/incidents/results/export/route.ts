import { forwardIncidentsRequest } from "@/lib/incidents-proxy";

export async function GET(request: Request) {
  return forwardIncidentsRequest(request, "/api/incidents/results/export");
}