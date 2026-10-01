import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";

import AppShell from "../components/layout/AppShell";
import PageHeader from "../components/ui/PageHeader";
import Card from "../components/ui/Card";
import ErrorState from "../components/ui/ErrorState";

import { getCaseRecommendations } from "../services/recommendationService";


function formatFeatureName(feature: string): string {
  return feature
    .replace(/_/g, " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}


export default function CaseRecommendationsPage() {
  const { id } = useParams<{ id: string }>();

  const recommendationsQuery = useQuery({
    queryKey: ["case-recommendations", id],
    queryFn: () => getCaseRecommendations(id!),
    enabled: Boolean(id),
  });

  return (
    <AppShell>
      <div className="space-y-6">
        <PageHeader
          title="Centre Recommendations"
          description="Explainable, non-clinical navigation recommendations based on verified centre data and case preferences."
        />

                <div>
          <Link
            to={`/cases/${id}`}
            className="text-sm font-medium text-blue-600 hover:underline"
          >
            ← Back to Case
          </Link>
        </div>

        <Card>
          <div className="p-6">
            <h2 className="text-lg font-semibold text-slate-900">
              How the Recommendation Score Is Calculated
            </h2>

            <p className="mt-2 text-sm text-slate-600">
              The current system uses a transparent, non-clinical navigation
              scoring baseline. The score is based on the following case and
              centre attributes:
            </p>

            <div className="mt-5 space-y-3">
              <div className="flex items-center justify-between rounded-lg border border-slate-200 px-4 py-3">
                <span className="text-sm font-medium text-slate-800">
                  Transplant Type Match
                </span>
                <span className="text-sm font-semibold text-slate-700">
                  60%
                </span>
              </div>

              <div className="flex items-center justify-between rounded-lg border border-slate-200 px-4 py-3">
                <span className="text-sm font-medium text-slate-800">
                  State Match
                </span>
                <span className="text-sm font-semibold text-slate-700">
                  25%
                </span>
              </div>

              <div className="flex items-center justify-between rounded-lg border border-slate-200 px-4 py-3">
                <span className="text-sm font-medium text-slate-800">
                  Preferred Region Match
                </span>
                <span className="text-sm font-semibold text-slate-700">
                  15%
                </span>
              </div>

              <div className="flex items-center justify-between border-t border-slate-300 pt-3">
                <span className="text-sm font-semibold text-slate-900">
                  Total
                </span>
                <span className="text-sm font-bold text-slate-900">
                  100%
                </span>
              </div>
            </div>

            <div className="mt-5 rounded-lg bg-slate-50 p-4">
              <p className="text-sm text-slate-600">
                This score supports centre navigation and does not determine
                transplant eligibility, treatment suitability, organ
                availability, or clinical outcomes. Final decisions require
                appropriate human and clinical review.
              </p>
            </div>
          </div>
        </Card>

        {recommendationsQuery.isLoading && (
  <div className="space-y-4">
    <div className="h-32 animate-pulse rounded-lg bg-slate-100" />
    <div className="h-32 animate-pulse rounded-lg bg-slate-100" />
    <div className="h-32 animate-pulse rounded-lg bg-slate-100" />
  </div>
)}

        {recommendationsQuery.isError && (
  <ErrorState
    message="The recommendation service could not return centre recommendations for this case."
  />
)}

        {recommendationsQuery.isSuccess &&
          recommendationsQuery.data.length === 0 && (
            <Card>
              <div className="p-6">
                <h2 className="text-lg font-semibold text-slate-900">
                  No recommendations available
                </h2>
                <p className="mt-2 text-sm text-slate-600">
                  No centres matched the available navigation data for this
                  case.
                </p>
              </div>
            </Card>
          )}

        {recommendationsQuery.isSuccess &&
          recommendationsQuery.data.length > 0 && (
            <div className="space-y-4">
              {recommendationsQuery.data.map((recommendation) => (
                <Card key={recommendation.centre_id}>
                  <div className="p-6">
                    <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                      <div>
                        <div className="flex items-center gap-3">
                          <span className="rounded-full bg-slate-100 px-3 py-1 text-sm font-semibold text-slate-700">
                            Rank #{recommendation.rank}
                          </span>

                          <span className="text-sm text-slate-500">
                            Score: {recommendation.score.toFixed(2)}
                          </span>
                        </div>

                        <h2 className="mt-3 text-xl font-semibold text-slate-900">
                          {recommendation.centre_name}
                        </h2>

                        <p className="mt-1 text-sm text-slate-600">
                          {[recommendation.city, recommendation.district, recommendation.state]
                            .filter(Boolean)
                            .join(", ")}
                        </p>
                      </div>

                      <Link
                        to={`/centres/${recommendation.centre_id}`}
                        className="text-sm font-medium text-blue-600 hover:underline"
                      >
                        View Centre
                      </Link>
                    </div>

                    <div className="mt-6">
                      <h3 className="text-sm font-semibold text-slate-900">
                        Why this centre was ranked here
                      </h3>

                      <div className="mt-3 space-y-3">
                        {recommendation.explanations.map((explanation) => (
                          <div
                            key={explanation.feature}
                            className="rounded-lg border border-slate-200 p-4"
                          >
                            <div className="flex items-center justify-between gap-4">
                              <span className="text-sm font-medium text-slate-800">
                                {formatFeatureName(explanation.feature)}
                              </span>

                              <span className="text-sm font-semibold text-slate-700">
                                +{explanation.contribution.toFixed(2)}
                              </span>
                            </div>

                            <p className="mt-1 text-sm text-slate-600">
                              {explanation.reason}
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="mt-6 border-t border-slate-200 pt-4">
                      <div className="flex flex-wrap gap-x-6 gap-y-2 text-xs text-slate-500">
                        <span>
                          Source: {recommendation.data_source ?? "Not specified"}
                        </span>

                        <span>
                          Verification: {recommendation.verification_status}
                        </span>

                        {recommendation.source_record_id !== null && (
                          <span>
                            Source record: {recommendation.source_record_id}
                          </span>
                        )}

                        {recommendation.source_dataset_version && (
                          <span>
                            Dataset: {recommendation.source_dataset_version}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}
      </div>
    </AppShell>
  );
}