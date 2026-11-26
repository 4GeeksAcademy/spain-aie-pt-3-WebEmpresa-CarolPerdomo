export const INCIDENT_CATEGORIES = [
  ["technical_failure", "Fallo técnico"],
  ["process_error", "Error de proceso"],
  ["client_complaint", "Queja de cliente"],
  ["candidate_issue", "Problema de candidato"],
  ["staff_issue", "Incidencia de personal"],
  ["sla_breach", "Incumplimiento de SLA"],
  ["data_quality", "Calidad de datos"],
  ["other", "Otro"],
] as const;

export const INCIDENT_STATUSES = [
  ["open", "Abierta"],
  ["in_progress", "En curso"],
  ["resolved", "Resuelta"],
  ["discarded", "Descartada"],
] as const;

export const INCIDENT_ORIGINS = [
  ["customer", "Cliente"],
  ["branch", "Oficina"],
  ["internal", "Interna"],
] as const;

export const INCIDENT_BRANCHES = [
  ["central", "Central — sede Valencia"],
  ["valencia_operations", "Valencia — Operaciones"],
  ["miami_office", "Miami Office"],
  ["remote", "Remoto"],
] as const;

export type IncidentStatus = (typeof INCIDENT_STATUSES)[number][0];
export type IncidentCategory = (typeof INCIDENT_CATEGORIES)[number][0];
export type IncidentOrigin = (typeof INCIDENT_ORIGINS)[number][0];
export type IncidentBranch = (typeof INCIDENT_BRANCHES)[number][0];

export type Incident = {
  id: number;
  title: string;
  description: string;
  category: IncidentCategory;
  status: IncidentStatus;
  origin: IncidentOrigin;
  branch: IncidentBranch;
  created_at: string;
  updated_at: string;
};

export type IncidentSummary = {
  total: number;
  by_status: Record<IncidentStatus, number>;
  by_category: Record<IncidentCategory, number>;
  by_origin: Record<IncidentOrigin, number>;
  by_branch: Record<IncidentBranch, number>;
};

export function incidentLabel(value: string, options: ReadonlyArray<readonly [string, string]>) {
  return options.find(([key]) => key === value)?.[1] ?? value;
}

export function incidentMessage(body: unknown, fallback: string) {
  if (body && typeof body === "object" && "detail" in body) {
    const detail = body.detail;
    if (typeof detail === "string") return detail;
    if (detail && typeof detail === "object" && "message" in detail && typeof detail.message === "string") {
      const firstError = "errors" in detail && Array.isArray(detail.errors) ? detail.errors[0] : null;
      if (firstError && typeof firstError === "object" && "field" in firstError && "message" in firstError) {
        const labels: Record<string, string> = {
          title: "Título", description: "Descripción", category: "Categoría",
          status: "Estado", origin: "Origen", branch: "Sede",
        };
        const field = String(firstError.field);
        return `${labels[field] ?? field}: ${String(firstError.message)}`;
      }
      return detail.message;
    }
  }
  return fallback;
}
