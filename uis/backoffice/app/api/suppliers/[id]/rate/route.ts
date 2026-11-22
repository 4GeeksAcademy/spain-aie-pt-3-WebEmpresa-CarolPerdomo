import { NextRequest } from "next/server";
import { proxySupplierRequest } from "@/lib/supplier-proxy";

type RouteContext = { params: Promise<{ id: string }> };

export async function PATCH(request: NextRequest, { params }: RouteContext) {
  const { id } = await params;
  return proxySupplierRequest(`/suppliers/${encodeURIComponent(id)}/rate`, {
    method: "PATCH",
    body: JSON.stringify(await request.json()),
  });
}
