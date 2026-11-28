import Link from "next/link";

const links = [
  ["Activos y stock", "/backoffice/inventory/products"],
  ["Registrar entrada", "/backoffice/inventory/orders/inbound"],
  ["Registrar salida", "/backoffice/inventory/orders/outbound"],
  ["Historial de órdenes", "/backoffice/inventory/orders"],
] as const;

export function InventoryNavigation() {
  return (
    <nav aria-label="Secciones de inventario" className="mt-6 overflow-x-auto border-b border-line">
      <ul className="flex min-w-max gap-2 pb-3">
        {links.map(([label, href]) => (
          <li key={href}>
            <Link
              href={href}
              className="inline-flex min-h-10 items-center rounded-lg border border-line bg-white px-3 py-2 text-sm font-semibold text-pine transition hover:border-pine hover:bg-pine/5 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-pine"
            >
              {label}
            </Link>
          </li>
        ))}
      </ul>
    </nav>
  );
}
