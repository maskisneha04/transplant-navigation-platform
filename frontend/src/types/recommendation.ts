export interface RecommendationExplanation {
  feature: string;
  contribution: number;
  reason: string;
}

export interface CentreRecommendation {
  centre_id: string;
  centre_name: string;
  city: string | null;
  district: string | null;
  state: string | null;
  score: number;
  rank: number;
  explanations: RecommendationExplanation[];
  verification_status: string;
  data_source: string | null;
  source_record_id: number | null;
  source_dataset_version: string | null;
}