import api from "./api";
import type {
  CentreDetail,
  CentreFilters,
  CentreListItem,
} from "../types/centre";

export async function listCentres(
  filters: CentreFilters = {},
): Promise<CentreListItem[]> {
  const { data } = await api.get<CentreListItem[]>("/centres", {
    params: filters,
  });

  return data;
}

export async function getCentre(
  centreId: string,
): Promise<CentreDetail> {
  const { data } = await api.get<CentreDetail>(
    `/centres/${centreId}`,
  );

  return data;
}