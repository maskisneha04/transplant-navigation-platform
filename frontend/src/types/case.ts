export type TransplantType = "KIDNEY" | "LIVER" | "HEART" | "LUNG" | "CORNEAL" | "BONE_MARROW";

export interface Preference {
  preference_key: string;
  preference_value: string;
}

export interface CaseCreateInput {
  transplant_type: string;
  location_city?: string;
  location_state?: string;
  preferred_region?: string;
  required_services?: string[];
  logistics_preferences?: Record<string, unknown>;
  case_description?: string;
  preferences?: Preference[];
}

export interface CaseUpdateInput {
  location_city?: string;
  location_state?: string;
  preferred_region?: string;
  required_services?: string[];
  case_description?: string;
}

export interface CaseDetail {
  id: string;
  patient_id: string;
  transplant_type: string;
  location_city: string | null;
  location_state: string | null;
  preferred_region: string | null;
  required_services: string[] | null;
  logistics_preferences: Record<string, unknown> | null;
  case_description: string | null;
  status: string;
  assigned_coordinator_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface CaseListItem {
  id: string;
  transplant_type: string;
  status: string;
  location_city: string | null;
  location_state: string | null;
  created_at: string;
  updated_at: string;
}

export interface TimelineEntry {
  id: string;
  from_status: string | null;
  to_status: string;
  changed_by: string;
  reason: string | null;
  created_at: string;
}
