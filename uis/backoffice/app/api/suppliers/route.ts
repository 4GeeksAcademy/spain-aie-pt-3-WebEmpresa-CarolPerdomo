import { NextRequest } from "next/server";
import { proxySupplierRequest } from "@/lib/supplier-proxy";

export function GET(request: NextRequest) {
  const query = request.nextUrl.search;
  return proxySupplierRequest(`/suppliers${query}`, {}, request.headers.get("authorization"));
}

export async function POST(request: NextRequest) {
  return proxySupplierRequest("/suppliers", {
    method: "POST",
    body: JSON.stringify(await request.json()),
  }, request.headers.get("authorization"));
}
