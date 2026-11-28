"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { getInventoryAssets, InventoryApiError, inventoryCategoryLabels, type InventoryAsset } from "@/lib/inventory";

function StockBadge({ stock }: { stock: number }) {
  // UX threshold: 1-3 units is low stock; zero is out of stock.
  const className = stock === 0
    ? "bg-red-100 text-red-800"
    : stock <= 3
      ? "bg-amber-100 text-amber-900"
      : "bg-emerald-100 text-emerald-900";
  const label = stock === 0 ? "Agotado" : stock <= 3 ? "Stock bajo" : "Disponible";
  return <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-semibold ${className}`}>{label}: {stock}</span>;
}

export function InventoryProducts() {
  const [assets, setAssets] = useState<InventoryAsset[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      setAssets(await getInventoryAssets());
    } catch (cause) {
      setError(cause instanceof InventoryApiError ? cause.message : "No se pudo conectar con el servicio de inventario.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const timer = window.setTimeout(() => { void load(); }, 0);
    return () => window.clearTimeout(timer);
  }, [load]);

  return (
    <section className="mt-8">
      <header className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="font-display text-4xl text-ink">Productos y stock</h1>
          <p className="mt-2 text-sm text-muted">Existencias actuales calculadas desde las órdenes registradas.</p>
        </div>
        <button type="button" onClick={() => void load()} className="min-h-10 rounded-lg border border-line bg-white px-4 py-2 text-sm font-semibold text-pine hover:bg-pine/5 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-pine">Actualizar</button>
      </header>
      {error && <div className="mt-5 rounded-lg border border-red-300 bg-red-50 p-4 text-sm text-red-800" role="alert">{error} <button type="button" className="ml-2 font-semibold underline" onClick={() => void load()}>Reintentar</button></div>}
      {loading ? <p className="mt-8" role="status">Cargando productos...</p> : error ? null : assets.length === 0 ? (
        <p className="mt-8 rounded-xl border border-line bg-white p-6 text-sm text-muted">Todavía no hay productos en el inventario.</p>
      ) : (
        <div className="mt-6 overflow-x-auto rounded-xl border border-line bg-white shadow-sm">
          <table className="w-full min-w-[760px] text-left text-sm">
            <thead className="bg-pine text-xs uppercase tracking-wide text-white"><tr><th className="px-4 py-3">Producto</th><th className="px-4 py-3">SKU</th><th className="px-4 py-3">Categoría</th><th className="px-4 py-3">Oficina</th><th className="px-4 py-3">Stock</th><th className="px-4 py-3">Acciones</th></tr></thead>
            <tbody className="divide-y divide-line">{assets.map((asset) => (
              <tr key={asset.id}>
                <td className="px-4 py-4 font-semibold">{asset.name}</td><td className="px-4 py-4">{asset.sku}</td><td className="px-4 py-4">{inventoryCategoryLabels[asset.category]}</td><td className="px-4 py-4">{asset.office}</td>
                <td className="px-4 py-4"><StockBadge stock={asset.current_stock} /></td>
                <td className="px-4 py-4"><div className="flex gap-3"><Link className="font-semibold text-pine underline" href={`/backoffice/inventory/orders/inbound?assetId=${asset.id}`}>Entrada</Link><Link className="font-semibold text-pine underline" href={`/backoffice/inventory/orders/outbound?assetId=${asset.id}`}>Salida</Link></div></td>
              </tr>
            ))}</tbody>
          </table>
        </div>
      )}
    </section>
  );
}
