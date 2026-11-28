"use client";

import { useCallback, useEffect, useMemo, useState, type FormEvent } from "react";
import { createInventoryInbound, createInventoryOutbound, getInventoryAssets, InventoryApiError, type InventoryAsset, type InventoryExitType } from "@/lib/inventory";

type Props = { mode: "inbound" | "outbound" };

export function InventoryOrderForm({ mode }: Props) {
  const inbound = mode === "inbound";
  const [assets, setAssets] = useState<InventoryAsset[]>([]);
  const [assetId, setAssetId] = useState("");
  const [quantity, setQuantity] = useState("");
  const [supplier, setSupplier] = useState("");
  const [exitType, setExitType] = useState<InventoryExitType>("allocation");
  const [assignedTo, setAssignedTo] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const loadAssets = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const result = await getInventoryAssets();
      setAssets(result);
      const requestedId = new URLSearchParams(window.location.search).get("assetId");
      if (requestedId && result.some((asset) => asset.id === Number(requestedId))) setAssetId(requestedId);
    } catch (cause) {
      setError(cause instanceof InventoryApiError ? cause.message : "No se pudo cargar la lista de productos.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const timer = window.setTimeout(() => { void loadAssets(); }, 0);
    return () => window.clearTimeout(timer);
  }, [loadAssets]);

  const selected = useMemo(() => assets.find((asset) => asset.id === Number(assetId)), [assets, assetId]);
  const requestedQuantity = Number(quantity);
  const insufficient = !inbound && selected !== undefined && requestedQuantity > 0 && requestedQuantity > selected.current_stock;

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setSuccess("");
    if (!selected) { setError("Selecciona un producto."); return; }
    if (!Number.isInteger(requestedQuantity) || requestedQuantity <= 0) { setError("La cantidad debe ser un número entero mayor que cero."); return; }
    if (inbound && !supplier.trim()) { setError("Indica el proveedor."); return; }
    if (!inbound && exitType === "allocation" && !assignedTo.trim()) { setError("Indica a quién se asigna el producto."); return; }
    setSaving(true);
    try {
      if (inbound) {
        await createInventoryInbound({ asset_id: selected.id, quantity: requestedQuantity, supplier: supplier.trim(), office: selected.office });
        setSuccess("La entrada se registró correctamente.");
        setQuantity("");
        setSupplier("");
      } else {
        await createInventoryOutbound({ asset_id: selected.id, quantity: requestedQuantity, exit_type: exitType, assigned_to: exitType === "allocation" ? assignedTo.trim() : null, office: selected.office });
        setSuccess("La salida se registró correctamente.");
        setQuantity("");
        setAssignedTo("");
        await loadAssets();
      }
    } catch (cause) {
      const message = cause instanceof InventoryApiError ? cause.message : "No se pudo completar la operación.";
      setError(message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="mt-8 max-w-3xl">
      <h1 className="font-display text-4xl text-ink">{inbound ? "Registrar entrada" : "Registrar salida"}</h1>
      <p className="mt-2 text-sm text-muted">{inbound ? "Añade al inventario una entrega recibida." : "Registra una asignación o consumo de stock."}</p>
      {error && <p className="mt-5 rounded-lg border border-red-300 bg-red-50 p-3 text-sm text-red-800" role="alert">{error}</p>}
      {success && <p className="mt-5 rounded-lg border border-emerald-300 bg-emerald-50 p-3 text-sm text-emerald-900" role="status">{success}</p>}
      {!loading && assets.length === 0 && error && <button type="button" onClick={() => void loadAssets()} className="mt-3 text-sm font-semibold text-pine underline">Reintentar carga de productos</button>}
      <form onSubmit={submit} className="mt-6 space-y-5 rounded-xl border border-line bg-white p-5 shadow-sm sm:p-7">
        <label className="block text-sm font-semibold">Producto
          <select required value={assetId} onChange={(event) => { setAssetId(event.target.value); setError(""); }} disabled={loading || saving} className="mt-2 min-h-11 w-full rounded-lg border border-line bg-white px-3 font-normal">
            <option value="">{loading ? "Cargando productos..." : "Selecciona un producto"}</option>
            {assets.map((asset) => <option key={asset.id} value={asset.id}>{asset.name} · {asset.sku} · {asset.office}{!inbound ? ` · Stock: ${asset.current_stock}` : ""}</option>)}
          </select>
        </label>
        {selected && <p className="text-sm text-muted">Oficina del activo: <strong className="text-ink">{selected.office}</strong>{!inbound && <> · Stock disponible: <strong className="text-ink">{selected.current_stock}</strong></>}</p>}
        {!inbound && <label className="block text-sm font-semibold">Tipo de salida
          <select value={exitType} onChange={(event) => setExitType(event.target.value as InventoryExitType)} disabled={saving} className="mt-2 min-h-11 w-full rounded-lg border border-line bg-white px-3 font-normal"><option value="allocation">Asignación a una persona</option><option value="consumption">Consumo</option></select>
        </label>}
        {!inbound && exitType === "allocation" && <label className="block text-sm font-semibold">Persona asignada
          <input required maxLength={160} value={assignedTo} onChange={(event) => setAssignedTo(event.target.value)} disabled={saving} className="mt-2 min-h-11 w-full rounded-lg border border-line px-3 font-normal" />
        </label>}
        {inbound && <label className="block text-sm font-semibold">Proveedor
          <input required maxLength={160} value={supplier} onChange={(event) => setSupplier(event.target.value)} disabled={saving} className="mt-2 min-h-11 w-full rounded-lg border border-line px-3 font-normal" />
        </label>}
        <label className="block text-sm font-semibold">Cantidad
          <input required min={1} step={1} type="number" value={quantity} onChange={(event) => { setQuantity(event.target.value); setError(""); }} disabled={saving} aria-describedby={insufficient ? "stock-warning" : !inbound && error ? "quantity-error" : undefined} aria-invalid={insufficient || (!inbound && Boolean(error)) || undefined} className="mt-2 min-h-11 w-full rounded-lg border border-line px-3 font-normal" />
        </label>
        {!inbound && insufficient && <p id="stock-warning" className="-mt-3 text-sm font-medium text-amber-800" role="status">La cantidad supera el stock disponible ({selected?.current_stock}). El servidor rechazará la salida si no hay existencias suficientes.</p>}
        {!inbound && error && <p id="quantity-error" className="-mt-3 text-sm text-red-800" role="alert">{error}</p>}
        <button type="submit" disabled={saving || loading || assets.length === 0} className="min-h-11 rounded-lg bg-pine px-5 py-2.5 font-semibold text-white hover:bg-pine/90 disabled:cursor-wait disabled:opacity-60">{saving ? "Guardando..." : inbound ? "Registrar entrada" : "Registrar salida"}</button>
      </form>
    </section>
  );
}
