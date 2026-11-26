import { SupplierDirectory } from "@/components/supplier-directory";

export const metadata = {
  title: "Supplier Directory | Nexova Backoffice",
  description: "Manage and track company suppliers",
};

export default function SuppliersPage() {
  return (
    <div className="py-8">
      <SupplierDirectory />
    </div>
  );
}
