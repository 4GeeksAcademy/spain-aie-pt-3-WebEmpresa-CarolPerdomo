import { NextRequest } from "next/server";
import { proxyApiRequest } from "@/lib/api-proxy";

export function GET(request: NextRequest) {
  return proxyApiRequest(request, "/profiles/me");
}

export function PUT(request: NextRequest) {
  return proxyApiRequest(request, "/profiles/me", "PUT");
}
