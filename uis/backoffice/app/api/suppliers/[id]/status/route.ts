import { NextRequest } from "next/server";
import { proxySupplierRequest } from "@/lib/supplier-proxy";
import { readJsonObject } from "@/lib/request-json";

type RouteContext = { params: Promise<{ id: string }> };

export async function PATCH(request: NextRequest, { params }: RouteContext) {
  const { id } = await params;
  const parsed = await readJsonObject(request);
  if (!parsed.ok) return parsed.response;
  return proxySupplierRequest(`/suppliers/${encodeURIComponent(id)}/status`, {
    method: "PATCH",
    body: JSON.stringify(parsed.value),
  }, request.headers.get("authorization"));
}
