"use client";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { CandidateForm } from "@/components/CandidateForm";
import { StatusBadge } from "@/components/StatusBadge";
import { api } from "@/lib/api";
import { candidateName, candidatePosition, stageLabels, stages, statusLabels, statuses, type Candidate, type Stage, type Status } from "@/types";

export default function Home() {
  const router = useRouter(); const pathname = usePathname(); const params = useSearchParams();
  const [candidates, setCandidates] = useState<Candidate[]>([]); const [loading, setLoading] = useState(true); const [error, setError] = useState(""); const [search, setSearch] = useState(""); const [showForm, setShowForm] = useState(false);
  const status = params.get("status") || ""; const stage = params.get("stage") || "";
  useEffect(() => { let active = true; api.getCandidates().then((data) => { if (active) setCandidates(data); }).catch((err) => { if (active) setError(err instanceof Error ? err.message : "No se pudieron cargar las candidaturas."); }).finally(() => { if (active) setLoading(false); }); return () => { active = false; }; }, []);
  const filtered = useMemo(() => candidates.filter((candidate) => (!status || candidate.status === status) && (!stage || candidate.stage === stage) && (!search || `${candidateName(candidate)} ${candidate.email}`.toLowerCase().includes(search.toLowerCase()))), [candidates, search, stage, status]);
  const filter = (key: "status" | "stage", value: string) => { const next = new URLSearchParams(params.toString()); if (value) next.set(key, value); else next.delete(key); router.replace(`${pathname}?${next.toString()}`); };
  return <main className="shell"><header className="topbar"><div><p className="eyebrow">NEXOVA / TALENT OPERATIONS</p><h1>Talent pipeline</h1></div><button className="button button-primary" onClick={() => setShowForm(true)}>+ Nueva candidatura</button></header>
    <section className="intro"><div><p className="eyebrow">PROCESO · ASISTENTE DE DIRECCIÓN</p><h2>El equipo correcto empieza aquí.</h2><p>Centraliza candidaturas, conversaciones y decisiones en un solo lugar.</p></div><div className="stat"><strong>{candidates.length}</strong><span>candidaturas totales</span></div></section>
    {showForm && <section className="panel form-panel"><div className="section-heading"><div><p className="eyebrow">NUEVO REGISTRO</p><h2>Añadir candidatura</h2></div></div><CandidateForm onDone={(candidate) => { setCandidates((current) => [candidate, ...current]); setShowForm(false); }} onCancel={() => setShowForm(false)} /></section>}
    <section className="panel"><div className="toolbar"><div><p className="eyebrow">BANDEJA DE CANDIDATURAS</p><h2>{filtered.length} perfiles visibles</h2></div><input className="search" aria-label="Buscar por nombre o email" placeholder="Buscar nombre o email..." value={search} onChange={(event) => setSearch(event.target.value)} /></div><div className="filters"><select aria-label="Filtrar por estado" value={status} onChange={(event) => filter("status", event.target.value)}><option value="">Todos los estados</option>{statuses.map((value: Status) => <option key={value} value={value}>{statusLabels[value]}</option>)}</select><select aria-label="Filtrar por etapa" value={stage} onChange={(event) => filter("stage", event.target.value)}><option value="">Todas las etapas</option>{stages.map((value: Stage) => <option key={value} value={value}>{stageLabels[value]}</option>)}</select></div>
      {loading && <div className="state">Cargando candidaturas...</div>}{!loading && error && <div className="state state-error" role="alert">{error}<button className="button button-quiet" onClick={() => window.location.reload()}>Reintentar</button></div>}{!loading && !error && filtered.length === 0 && <div className="state">No hay candidaturas que coincidan con estos filtros.</div>}
      {!loading && !error && filtered.length > 0 && <div className="candidate-list">{filtered.map((candidate) => <Link className="candidate-row" href={`/candidates/${candidate.id}`} key={candidate.id}><div className="avatar">{candidateName(candidate).slice(0, 1).toUpperCase()}</div><div className="candidate-main"><strong>{candidateName(candidate)}</strong><span>{candidate.email}</span></div><div className="candidate-position">{candidatePosition(candidate)}</div><StatusBadge value={candidate.status} /><StatusBadge value={candidate.stage} kind="stage" /><span className="row-arrow">→</span></Link>)}</div>}
    </section>
  </main>;
}
