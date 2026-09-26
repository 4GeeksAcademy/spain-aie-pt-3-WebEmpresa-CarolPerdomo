"use client";

import { useState } from "react";
import { departments, companyMetrics, operationalAreas, supportSlaGapHours } from "@/lib/dashboard-data";
import { MetricCard } from "@/components/metric-card";
import { Sidebar } from "@/components/sidebar";

const statusStyles = {
  critical: "border-coral/40 bg-coral/10 text-[#a44734]",
  attention: "border-[#c3a654]/50 bg-[#f7f0d8] text-[#78611c]",
  neutral: "border-line bg-paper text-muted",
};

type AreaTone = keyof typeof statusStyles;

export function DashboardHome() {
  const [selectedDepartment, setSelectedDepartment] = useState("Todas");
  const [searchTerm, setSearchTerm] = useState("");
  const filteredAreas = operationalAreas.filter((area) => {
    const matchesDepartment = selectedDepartment === "Todas" || area.department === selectedDepartment;
    const searchableText = `${area.department} ${area.issue} ${area.signal}`.toLocaleLowerCase("es");
    return matchesDepartment && searchableText.includes(searchTerm.trim().toLocaleLowerCase("es"));
  });

  return (
    <div className="min-h-screen lg:grid lg:grid-cols-[248px_minmax(0,1fr)]">
      <Sidebar />
      <main id="resumen" className="min-w-0 px-4 pb-16 pt-7 sm:px-7 lg:px-10 lg:pt-10">
        <header className="flex flex-col gap-3 border-b border-line pb-6 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-[0.65rem] font-semibold uppercase tracking-[0.16em] text-coral">
              Dirección ejecutiva
            </p>
            <h1 className="mt-2 font-display text-4xl leading-tight text-ink sm:text-5xl">
              Panel de Nexova
            </h1>
          </div>
          <p className="text-xs text-muted">Indicadores de referencia · Briefing de empresa</p>
        </header>

        <section aria-label="Indicadores de empresa" className="grid grid-cols-2 gap-3 py-6 lg:grid-cols-4 lg:gap-4 lg:py-8">
          {companyMetrics.map((metric) => (
            <MetricCard key={metric.label} {...metric} />
          ))}
        </section>

        <section id="operaciones" aria-labelledby="operations-title" className="scroll-mt-6">
          <div className="flex flex-col gap-4 border-b border-line pb-4 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <p className="text-[0.65rem] font-semibold uppercase tracking-[0.16em] text-coral">
                Pulso operativo
              </p>
              <h2 id="operations-title" className="mt-2 font-display text-3xl text-ink">
                Señales por área
              </h2>
            </div>
            <div className="grid gap-3 sm:grid-cols-[minmax(190px,1fr)_minmax(190px,1fr)]">
              <div>
                <label htmlFor="department-filter" className="sr-only">Filtrar por área</label>
                <select
                  id="department-filter"
                  value={selectedDepartment}
                  onChange={(event) => setSelectedDepartment(event.target.value)}
                  className="min-h-11 w-full border border-line bg-white px-3 text-sm text-ink focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-coral"
                >
                  {departments.map((department) => (
                    <option key={department} value={department}>{department}</option>
                  ))}
                </select>
              </div>
              <div>
                <label htmlFor="area-search" className="sr-only">Buscar señales operativas</label>
                <input
                  id="area-search"
                  type="search"
                  value={searchTerm}
                  onChange={(event) => setSearchTerm(event.target.value)}
                  placeholder="Buscar en las áreas"
                  className="min-h-11 w-full border border-line bg-white px-3 text-sm text-ink placeholder:text-muted focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-coral"
                />
              </div>
            </div>
          </div>

          <p className="py-3 text-xs text-muted" aria-live="polite">
            {filteredAreas.length} de {operationalAreas.length} áreas visibles
          </p>
          {filteredAreas.length > 0 ? (
            <ul className="divide-y divide-line" aria-label="Señales operativas por área">
              {filteredAreas.map((area) => (
                <li key={area.department} className="py-4 sm:py-5">
                  <article className="grid gap-3 sm:grid-cols-[minmax(145px,0.7fr)_minmax(190px,1.2fr)_minmax(200px,1.6fr)_auto] sm:items-center sm:gap-5">
                    <div>
                      <h3 className="font-semibold text-ink">{area.department}</h3>
                      <p className="mt-1 text-xs text-muted">{area.team}</p>
                    </div>
                    <p className="text-sm font-medium text-ink">{area.issue}</p>
                    <p className="text-sm leading-5 text-muted">{area.signal}</p>
                    <span className={`w-fit border px-2.5 py-1 text-[0.65rem] font-semibold ${statusStyles[area.tone as AreaTone]}`}>
                      {area.status}
                    </span>
                  </article>
                </li>
              ))}
            </ul>
          ) : (
            <p className="py-12 text-center text-sm text-muted">No hay áreas que coincidan con la búsqueda.</p>
          )}
        </section>

        <section id="prioridades" aria-labelledby="priorities-title" className="mt-10 border-t border-line pt-8">
          <div className="grid gap-8 md:grid-cols-[0.7fr_1.3fr]">
            <div>
              <p className="text-[0.65rem] font-semibold uppercase tracking-[0.16em] text-coral">
                Atención prioritaria
              </p>
              <h2 id="priorities-title" className="mt-2 font-display text-3xl text-ink">
                El siguiente paso
              </h2>
            </div>
            <div className="border-l-2 border-coral pl-5">
              <p className="text-sm font-semibold text-ink">Cerrar la brecha del SLA de soporte</p>
              <p className="mt-2 max-w-2xl text-sm leading-6 text-muted">
                La resolución media es de 48 horas frente a un compromiso de 24.
                La diferencia calculada es de {supportSlaGapHours} horas; centralizar
                conocimiento y dar visibilidad al backlog son necesidades señaladas
                en el briefing.
              </p>
              <p className="mt-3 text-xs font-semibold text-coral">+{supportSlaGapHours} h sobre el compromiso</p>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}