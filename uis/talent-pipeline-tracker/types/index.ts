export type Status = "received" | "in_progress" | "selected" | "discarded";
export type Stage = "pending" | "review" | "personal_interview" | "technical_interview" | "offer_presented";

export interface Candidate {
  id: number;
  name: string;
  full_name?: string;
  email: string;
  phone?: string;
  position?: string;
  job_title?: string;
  linkedin?: string;
  linkedin_url?: string;
  resume_url?: string;
  cv_url?: string;
  years_experience?: number;
  status: Status;
  stage: Stage;
  applied_at?: string;
  created_at?: string;
}
export interface CandidatePayload {
  name: string; email: string; phone: string; position: string; linkedin: string;
  resume_url: string; years_experience: number; status: Status; stage: Stage;
}
export interface Note { id: number; content: string; created_at?: string; }
export const statusLabels: Record<Status, string> = { received: "Recibida", in_progress: "En proceso", selected: "Seleccionada", discarded: "Descartada" };
export const stageLabels: Record<Stage, string> = { pending: "Pendiente de revisión", review: "En revisión", personal_interview: "Entrevista personal", technical_interview: "Entrevista técnica", offer_presented: "Oferta presentada" };
export const statuses = Object.keys(statusLabels) as Status[];
export const stages = Object.keys(stageLabels) as Stage[];
export const candidateName = (candidate: Candidate) => candidate.full_name || candidate.name;
export const candidatePosition = (candidate: Candidate) => candidate.position || candidate.job_title || "Sin puesto";
