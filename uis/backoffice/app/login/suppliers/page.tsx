import { redirect } from "next/navigation";

export default function LegacySuppliersRedirect() {
  redirect("/suppliers");
}
