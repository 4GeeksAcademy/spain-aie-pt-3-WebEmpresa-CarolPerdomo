import { Sidebar } from "@/components/sidebar";
import { InventoryNavigation } from "@/components/inventory-navigation";

export default function InventoryLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen lg:grid lg:grid-cols-[248px_minmax(0,1fr)]">
      <Sidebar active="inventario" />
      <main className="min-w-0 px-4 pb-16 pt-7 sm:px-7 lg:px-10 lg:py-10">
        <div className="mx-auto max-w-7xl">
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-muted">Operaciones · Inventario</p>
          <InventoryNavigation />
          {children}
        </div>
      </main>
    </div>
  );
}
