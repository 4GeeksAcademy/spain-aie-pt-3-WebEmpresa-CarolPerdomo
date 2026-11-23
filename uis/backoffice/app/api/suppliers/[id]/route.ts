import { NextRequest } from "next/server";
import { proxySupplierRequest } from "@/lib/supplier-proxy";

type RouteContext = { params: Promise<{ id: string }> };

export async function GET(request: NextRequest, { params }: RouteContext) {
  const { id } = await params;
  return proxySupplierRequest(`/suppliers/${encodeURIComponent(id)}`, {}, request.headers.get("authorization"));
}

export async function DELETE(request: NextRequest, { params }: RouteContext) {
  const { id } = await params;
  return proxySupplierRequest(`/suppliers/${encodeURIComponent(id)}`, { method: "DELETE" }, request.headers.get("authorization"));
}
