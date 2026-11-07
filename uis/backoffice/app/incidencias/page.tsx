import { IncidentAnalysis } from "@/components/incident-analysis";
import { Sidebar } from "@/components/sidebar";

export default function IncidentsPage() {
  return (
    <div className="min-h-screen lg:grid lg:grid-cols-[248px_minmax(0,1fr)]">
      <Sidebar active="incidencias" />
      <IncidentAnalysis />
    </div>
  );
}