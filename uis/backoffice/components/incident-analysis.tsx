"use client";

import { useState, type FormEvent } from "react";

type Analysis = {
  analysis_id: string;
  total: number;
  valid: number;
  invalid: number;
  issues: Record<string, { label: string; count: number }>;
  categories: Record<string, number>;
  statuses: Record<string, number>;
  satisfaction: { scored: number; closed: number; average: number | null; scores: Record<string, number> };
};

function Breakdown({ title, values, total }: { title: string; values: Record<string, number>; total: number }) {
  return (
    <section aria-label={title} className="min-w-0 border-t border-line pt-5">
      <h2 className="font-display text-2xl text-ink">{title}</h2>
      <dl className="mt-4 divide-y divide-line">
        {Object.entries(values).map(([label, count]) => (
          <div key={label} className="flex items-center justify-between gap-4 py-3 text-sm">
            <dt className="font-semibold text-ink">{label}</dt>
            <dd className="shrink-0 tabular-nums text-muted">{count} <span className="ml-2">({total ? (count / total * 100).toFixed(1) : "0.0"}%)</span></dd>
          </div>
        ))}
      </dl>
    </section>
  );
}

export function IncidentAnalysis() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<Analysis | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const data = new FormData();
      data.append("file", file);
      const response = await fetch("/api/incidents/analyze", { method: "POST", body: data });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || "No se pudo analizar el archivo.");
      setResult(payload as Analysis);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "No se pudo analizar el archivo.");
    } finally {
      setLoading(false);
    }
  }

  async function download() {
    if (!result) return;
    setError("");
    try {
      const response = await fetch("/api/incidents/results/export", { cache: "no-store", headers: { "If-Match": result.analysis_id } });
      if (!response.ok) {
        const payload = await response.json();
        throw new Error(payload.error || "No se pudo descargar el informe.");
      }
      const url = URL.createObjectURL(await response.blob());
      const link = document.createElement("a");
      link.href = url;
      link.download = "results.csv";
      link.click();
      URL.revokeObjectURL(url);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "No se pudo descargar el informe.");
    }
  }

  return (
    <main className="min-w-0 px-4 pb-16 pt-7 sm:px-7 lg:px-10 lg:pt-10">
      <header className="border-b border-line pb-6">
        <p className="text-xs font-semibold uppercase text-coral">Atención al cliente</p>
        <h1 className="mt-2 font-display text-4xl leading-tight text-ink sm:text-5xl">Análisis de incidencias</h1>
      </header>

      <form onSubmit={submit} className="flex flex-col gap-4 border-b border-line py-6 sm:flex-row sm:items-end">
        <div className="min-w-0 flex-1">
          <label htmlFor="incident-file" className="block text-sm font-semibold text-ink">Archivo CSV de incidencias</label>
          <input id="incident-file" type="file" accept=".csv,text/csv" required onChange={(event) => setFile(event.target.files?.[0] ?? null)} className="mt-2 block w-full min-w-0 text-sm text-muted file:mr-3 file:border-0 file:bg-pine file:px-4 file:py-2.5 file:font-semibold file:text-white focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-coral" />
        </div>
        <button type="submit" disabled={loading || !file} className="min-h-11 bg-coral px-5 text-sm font-semibold text-white hover:bg-[#a44734] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-coral disabled:cursor-not-allowed disabled:opacity-50">{loading ? "Analizando..." : "Analizar archivo"}</button>
      </form>
      <p role="status" className="min-h-6 pt-2 text-sm text-muted">{loading ? "Analizando incidencias..." : result ? "Análisis completado." : ""}</p>
      {error && <p role="alert" className="border-l-2 border-coral py-2 pl-3 text-sm text-[#9b3828]">{error}</p>}

      {result && (
        <>
          <section aria-label="Resumen del análisis" className="grid grid-cols-2 gap-3 py-6 lg:grid-cols-4">
            {[["Registros", result.total], ["Válidos", result.valid], ["Inválidos", result.invalid], ["Satisfacción media", result.satisfaction.average === null ? "Sin datos" : `${result.satisfaction.average.toFixed(2)} / 5`]].map(([label, value]) => (
              <div key={label} className="border border-line bg-white p-4">
                <p className="text-xs font-semibold uppercase text-muted">{label}</p>
                <p className="mt-2 text-2xl font-semibold tabular-nums text-ink">{value}</p>
              </div>
            ))}
          </section>

          <div className="grid gap-8 md:grid-cols-2">
            <Breakdown title="Categorías" values={result.categories} total={result.valid} />
            <Breakdown title="Estados" values={result.statuses} total={result.valid} />
            <section className="border-t border-line pt-5">
              <h2 className="font-display text-2xl text-ink">Satisfacción</h2>
              <p className="mt-3 text-sm text-muted">{result.satisfaction.scored} de {result.satisfaction.closed} incidencias cerradas con puntuación</p>
              <dl className="mt-3 divide-y divide-line">
                {Object.entries(result.satisfaction.scores).map(([score, count]) => <div key={score} className="flex justify-between gap-4 py-2 text-sm"><dt>Puntuación {score}</dt><dd className="tabular-nums">{count}</dd></div>)}
              </dl>
            </section>
            <section className="border-t border-line pt-5">
              <h2 className="font-display text-2xl text-ink">Registros inválidos</h2>
              <p className="mt-3 text-sm text-muted">{result.invalid} registros con errores; un registro puede tener varios motivos.</p>
              <dl className="mt-3 divide-y divide-line">
                {Object.entries(result.issues).filter(([, issue]) => issue.count > 0).map(([key, issue]) => <div key={key} className="flex justify-between gap-4 py-2 text-sm"><dt>{issue.label}</dt><dd className="tabular-nums">{issue.count}</dd></div>)}
              </dl>
            </section>
          </div>
          <button type="button" onClick={download} className="mt-8 min-h-11 border border-pine px-5 text-sm font-semibold text-pine hover:bg-pine hover:text-white focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-coral">Descargar CSV</button>
        </>
      )}
    </main>
  );
}