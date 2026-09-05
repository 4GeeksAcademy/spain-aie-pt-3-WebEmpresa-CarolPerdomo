"use client";
import { useState } from "react";
import { api } from "@/lib/api";
import { stages, statusLabels, statuses, stageLabels, type Candidate, type CandidatePayload, type Stage, type Status } from "@/types";

const empty: CandidatePayload = { name: "", email: "", phone: "", position: "Asistente de Dirección", linkedin: "", resume_url: "", years_experience: 0, status: "received", stage: "pending" };

export function CandidateForm({ candidate, onDone, onCancel }: { candidate?: Candidate; onDone: (candidate: Candidate) => void; onCancel?: () => void }) {
  const [form, setForm] = useState<CandidatePayload>(candidate ? { name: candidate.name || candidate.full_name || "", email: candidate.email, phone: candidate.phone || "", position: candidate.position || candidate.job_title || "", linkedin: candidate.linkedin || candidate.linkedin_url || "", resume_url: candidate.resume_url || candidate.cv_url || "", years_experience: candidate.years_experience || 0, status: candidate.status, stage: candidate.stage } : empty);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const change = (key: keyof CandidatePayload, value: string | number) => setForm((current) => ({ ...current, [key]: value }));
  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!form.name.trim() || !form.email.trim() || !form.position.trim()) { setError("Nombre, email y puesto son obligatorios."); return; }
    if (form.years_experience < 0 || form.years_experience > 50) { setError("Los años de experiencia deben estar entre 0 y 50."); return; }
    setSaving(true); setError("");
    try { const result = candidate ? await api.replaceCandidate(candidate.id, form) : await api.createCandidate(form); onDone(result); }
    catch (err) { setError(err instanceof Error ? err.message : "No se pudo guardar la candidatura."); }
    finally { setSaving(false); }
  };
  const textFields: Array<[keyof CandidatePayload, string, string]> = [["name", "Nombre completo", "text"], ["email", "Email", "email"], ["phone", "Teléfono", "tel"], ["position", "Puesto", "text"], ["linkedin", "LinkedIn", "url"], ["resume_url", "Enlace al CV", "url"]];
  return <form className="candidate-form" onSubmit={submit}>
    <div className="form-grid">
      {textFields.map(([key, label, type]) => <label key={key}>{label}<input required={key === "name" || key === "email" || key === "position"} type={type} value={form[key] as string} onChange={(event) => change(key, event.target.value)} /></label>)}
      <label>Años de experiencia<input type="number" min="0" max="50" value={form.years_experience} onChange={(event) => change("years_experience", Number(event.target.value))} /></label>
      <label>Estado<select value={form.status} onChange={(event) => change("status", event.target.value as Status)}>{statuses.map((value) => <option key={value} value={value}>{statusLabels[value]}</option>)}</select></label>
      <label>Etapa<select value={form.stage} onChange={(event) => change("stage", event.target.value as Stage)}>{stages.map((value) => <option key={value} value={value}>{stageLabels[value]}</option>)}</select></label>
    </div>
    {error && <p className="form-error" role="alert">{error}</p>}
    <div className="form-actions"><button className="button button-primary" disabled={saving}>{saving ? "Guardando..." : candidate ? "Guardar cambios" : "Registrar candidatura"}</button>{onCancel && <button type="button" className="button button-quiet" onClick={onCancel}>Cancelar</button>}</div>
  </form>;
}
