"use client";

import { apiFetch } from "@/lib/auth-client";

export type InventoryCategory = "hardware" | "peripherals" | "office_supplies" | "training_materials";
export type InventoryOffice = "Valencia" | "Miami";
export type InventoryExitType = "allocation" | "consumption";

export type InventoryAsset = {
  id: number;
  name: string;
  sku: string;
  category: InventoryCategory;
  office: InventoryOffice;
  current_stock: number;
};

export type InventoryOrder = {
  id: number;
  order_type: "inbound" | "outbound";
  asset_id: number;
  asset_name: string;
  sku: string;
  quantity: number;
  supplier?: string | null;
  exit_type?: InventoryExitType | null;
  assigned_to?: string | null;
  office: InventoryOffice;
  created_at: string;
  user_uuid: string;
};

export type InventoryInboundPayload = {
  asset_id: number;
  quantity: number;
  supplier: string;
  office: InventoryOffice;
};

export type InventoryOutboundPayload = {
  asset_id: number;
  quantity: number;
  exit_type: InventoryExitType;
  assigned_to: string | null;
  office: InventoryOffice;
};

export class InventoryApiError extends Error {
  constructor(message: string, public readonly status: number) {
    super(message);
    this.name = "InventoryApiError";
  }
}

export const inventoryCategoryLabels: Record<InventoryCategory, string> = {
  hardware: "Hardware",
  peripherals: "Periféricos",
  office_supplies: "Material de oficina",
  training_materials: "Material de formación",
};

const API_BASE = (process.env.NEXT_PUBLIC_INVENTORY_API_URL || "http://localhost:8000").replace(/\/+$/, "");

function messageFrom(body: unknown, status: number): string {
  if (body && typeof body === "object") {
    const detail = (body as { detail?: unknown }).detail;
    if (typeof detail === "string" && detail.trim()) return detail;
    if (Array.isArray(detail)) {
      const messages = detail.flatMap((item) => {
        if (item && typeof item === "object" && "msg" in item && typeof item.msg === "string") return [item.msg];
        return [];
      });
      if (messages.length) return messages.join(" ");
    }
    const message = (body as { message?: unknown }).message;
    if (typeof message === "string" && message.trim()) return message;
  }
  return `No se pudo completar la operación de inventario (HTTP ${status}).`;
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  if (init.body && !headers.has("Content-Type")) headers.set("Content-Type", "application/json");

  const response = await apiFetch(`${API_BASE}/inventory${path}`, { ...init, headers });
  const body: unknown = response.status === 204 ? null : await response.json().catch(() => null);
  if (!response.ok) throw new InventoryApiError(messageFrom(body, response.status), response.status);
  return body as T;
}

export function getInventoryAssets() {
  return request<InventoryAsset[]>("/products");
}

export function getInventoryOrders() {
  return request<InventoryOrder[]>("/orders");
}

export function createInventoryInbound(payload: InventoryInboundPayload) {
  return request<unknown>("/orders/inbound", { method: "POST", body: JSON.stringify(payload) });
}

export function createInventoryOutbound(payload: InventoryOutboundPayload) {
  return request<unknown>("/orders/outbound", { method: "POST", body: JSON.stringify(payload) });
}
