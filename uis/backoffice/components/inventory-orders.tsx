"use client";

import { useCallback, useEffect, useState } from "react";
import { getInventoryOrders, InventoryApiError, type InventoryOrder } from "@/lib/inventory";

function formatDate(value: string) {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : new Intl.DateTimeFormat("es-ES", { dateStyle: "medium", timeStyle: "short", timeZone: "UTC" }).format(date) + " UTC";
}

export function InventoryOrders() {
  const [orders, setOrders] = useState<InventoryOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try { setOrders(await getInventoryOrders()); }
    catch (cause) { setError(cause instanceof InventoryApiError ? cause.message : "No se pudo cargar el historial de órdenes."); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => {
    const timer = window.setTimeout(() => { void load(); }, 0);
    return () => window.clearTimeout(timer);
  }, [load]);

  return (
    <section className="mt-8">
      <header className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div><h1 className="font-display text-4xl text-ink">Historial de órdenes</h1><p className="mt-2 text-sm text-muted">Registro de entradas y salidas de inventario. Esta vista es de solo lectura.</p></div>
        <button type="button" onClick={() => void load()} className="min-h-10 rounded-lg border border-line bg-white px-4 py-2 text-sm font-semibold text-pine hover:bg-pine/5">Actualizar</button>
      </header>
      {error && <p className="mt-5 rounded-lg border border-red-300 bg-red-50 p-4 text-sm text-red-800" role="alert">{error} <button type="button" className="font-semibold underline" onClick={() => void load()}>Reintentar</button></p>}
      {loading ? <p className="mt-8" role="status">Cargando historial...</p> : error ? null : orders.length === 0 ? <p className="mt-8 rounded-xl border border-line bg-white p-6 text-sm text-muted">Todavía no hay órdenes registradas.</p> : (
        <div className="mt-6 overflow-x-auto rounded-xl border border-line bg-white shadow-sm">
          <table className="w-full min-w-[900px] text-left text-sm">
            <thead className="bg-pine text-xs uppercase tracking-wide text-white"><tr><th className="px-4 py-3">Movimiento</th><th className="px-4 py-3">Producto</th><th className="px-4 py-3">Cantidad</th><th className="px-4 py-3">Detalle</th><th className="px-4 py-3">Oficina</th><th className="px-4 py-3">Fecha (UTC)</th><th className="px-4 py-3">Registrado por (UUID)</th></tr></thead>
            <tbody className="divide-y divide-line">{orders.map((order) => {
              const isInbound = order.order_type === "inbound";
              return <tr key={`${order.order_type}-${order.id}`}>
                <td className="px-4 py-4"><span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-semibold ${isInbound ? "bg-emerald-100 text-emerald-900" : "bg-violet-100 text-violet-900"}`}>{isInbound ? "Entrada" : "Salida"}</span></td>
                <td className="px-4 py-4"><p className="font-semibold">{order.asset_name}</p><p className="text-xs text-muted">{order.sku}</p></td><td className="px-4 py-4 font-semibold">{order.quantity}</td>
                <td className="px-4 py-4">{isInbound ? `Proveedor: ${order.supplier || "—"}` : order.exit_type === "allocation" ? `Asignado a: ${order.assigned_to || "—"}` : "Consumo"}</td>
                <td className="px-4 py-4">{order.office}</td><td className="px-4 py-4">{formatDate(order.created_at)}</td><td className="max-w-64 break-all px-4 py-4 font-mono text-xs">{order.user_uuid}</td>
              </tr>;
            })}</tbody>
          </table>
        </div>
      )}
    </section>
  );
}
