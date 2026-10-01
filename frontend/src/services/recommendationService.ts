import api from "./api";
import type { CentreRecommendation } from "../types/recommendation";

export async function getCaseRecommendations(
  caseId: string,
): Promise<CentreRecommendation[]> {
  const { data } = await api.get<CentreRecommendation[]>(
    `/cases/${caseId}/recommendations`,
  );

  return data;
}