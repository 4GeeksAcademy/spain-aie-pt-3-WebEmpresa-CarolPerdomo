import { NextRequest } from "next/server";
import { proxySupplierRequest } from "@/lib/supplier-proxy";
import { readJsonObject } from "@/lib/request-json";

export function GET(request: NextRequest) {
  const query = request.nextUrl.search;
  return proxySupplierRequest(`/suppliers${query}`, {}, request.headers.get("authorization"));
}

export async function POST(request: NextRequest) {
  const parsed = await readJsonObject(request);
  if (!parsed.ok) return parsed.response;
  return proxySupplierRequest("/suppliers", {
    method: "POST",
    body: JSON.stringify(parsed.value),
  }, request.headers.get("authorization"));
}
