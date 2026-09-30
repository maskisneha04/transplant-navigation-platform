import api from "./api";
import type { CaseCreateInput, CaseUpdateInput, CaseDetail, CaseListItem, TimelineEntry } from "../types/case";

export async function createCase(input: CaseCreateInput): Promise<CaseDetail> {
  const { data } = await api.post<CaseDetail>("/cases", input);
  return data;
}

export async function listCases(): Promise<CaseListItem[]> {
  const { data } = await api.get<CaseListItem[]>("/cases");
  return data;
}

export async function getCase(caseId: string): Promise<CaseDetail> {
  const { data } = await api.get<CaseDetail>(`/cases/${caseId}`);
  return data;
}

export async function updateCase(caseId: string, input: CaseUpdateInput): Promise<CaseDetail> {
  const { data } = await api.patch<CaseDetail>(`/cases/${caseId}`, input);
  return data;
}

export async function changeCaseStatus(caseId: string, newStatus: string, reason?: string): Promise<CaseDetail> {
  const { data } = await api.post<CaseDetail>(`/cases/${caseId}/status`, { new_status: newStatus, reason });
  return data;
}

export async function getCaseTimeline(caseId: string): Promise<TimelineEntry[]> {
  const { data } = await api.get<TimelineEntry[]>(`/cases/${caseId}/timeline`);
  return data;
}
