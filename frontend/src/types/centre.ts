export interface CentreListItem {
  id: string;
  name: string;
  city: string | null;
  district: string | null;
  state: string | null;
  registration_type: string | null;
  transplant_types: string[] | null;
  verification_status: string;
  data_source: string | null;
  last_verified_at: string | null;
}

export interface CentreDetail extends CentreListItem {
  address: string | null;
  raw_organ_tissue_type: string | null;
  details: string | null;
  website: string | null;
  capability_score: number | null;
  logistics_score: number | null;
  source_record_id: number | null;
  source_dataset_version: string | null;
}

export interface CentreFilters {
  search?: string;
  state?: string;
  transplant_type?: string;
  registration_type?: string;
  skip?: number;
  limit?: number;
}