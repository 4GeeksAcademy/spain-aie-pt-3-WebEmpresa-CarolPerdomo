import type { Candidate, CandidatePayload, Note } from "@/types";
const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://playground.4geeks.com/tracker/api/v1";
async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, { ...options, headers: { "Content-Type": "application/json", ...options?.headers } });
  if (!response.ok) throw new Error((await response.text()) || `La petición falló (${response.status})`);
  if (response.status === 204) return undefined as T;
  return response.json();
}
function unwrap<T>(value: T | { records?: T; data?: T; notes?: T }): T {
  if (value && typeof value === "object") { const wrapped = value as { records?: T; data?: T; notes?: T }; return (wrapped.records || wrapped.data || wrapped.notes || value) as T; }
  return value as T;
}
export const api = {
  async getCandidates() { return unwrap(await request<Candidate[] | { records: Candidate[] }>("/records")) || []; },
  async getCandidate(id: string) { return unwrap(await request<Candidate | { data: Candidate }>(`/records/${id}`)); },
  updateCandidate(id: number, payload: Partial<CandidatePayload>) { return request<Candidate>(`/records/${id}`, { method: "PATCH", body: JSON.stringify(payload) }); },
  replaceCandidate(id: number, payload: CandidatePayload) { return request<Candidate>(`/records/${id}`, { method: "PUT", body: JSON.stringify(payload) }); },
  createCandidate(payload: CandidatePayload) { return request<Candidate>("/records", { method: "POST", body: JSON.stringify(payload) }); },
  async getNotes(id: string) { return unwrap(await request<Note[] | { notes: Note[] }>(`/records/${id}/notes`)) || []; },
  addNote(id: string, content: string) { return request<Note>(`/records/${id}/notes`, { method: "POST", body: JSON.stringify({ content }) }); },
  removeNote(id: string, noteId: number) { return request<void>(`/records/${id}/notes/${noteId}`, { method: "DELETE" }); },
};
