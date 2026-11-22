import { proxySupplierRequest } from "@/lib/supplier-proxy";

type RouteContext = { params: Promise<{ id: string }> };

export async function DELETE(_request: Request, { params }: RouteContext) {
  const { id } = await params;
  return proxySupplierRequest(`/suppliers/${encodeURIComponent(id)}`, { method: "DELETE" });
}
