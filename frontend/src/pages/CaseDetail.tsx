import { useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";

import AppShell from "../components/layout/AppShell";
import PageHeader from "../components/ui/PageHeader";
import Card, { CardBody, CardHeader } from "../components/ui/Card";
import Button from "../components/ui/Button";
import StatusBadge from "../components/ui/StatusBadge";
import ErrorState from "../components/ui/ErrorState";
import ConfirmDialog from "../components/ui/ConfirmDialog";
import { SkeletonCard } from "../components/ui/Skeleton";
import { useToast } from "../components/ui/Toast";

import {
  getCase,
  getCaseTimeline,
  changeCaseStatus,
} from "../services/caseService";

import { extractErrorMessage } from "../services/authService";

import {
  TRANSPLANT_TYPE_LABELS,
  STATUS_META,
  type CaseStatus,
} from "../constants/status";


function formatDateTime(iso: string) {
  return new Date(iso).toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}


const CANCELLABLE_STATUSES = new Set([
  "NEW",
  "DOCUMENT_COLLECTION",
  "UNDER_REVIEW",
  "COORDINATOR_REVIEW",
  "CENTRE_REVIEW",
]);


export default function CaseDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { showToast } = useToast();

  const [confirmCancelOpen, setConfirmCancelOpen] = useState(false);
  const [cancelling, setCancelling] = useState(false);


  const caseQuery = useQuery({
    queryKey: ["case", id],
    queryFn: () => getCase(id!),
    enabled: Boolean(id),
    retry: false,
  });


  const timelineQuery = useQuery({
    queryKey: ["case-timeline", id],
    queryFn: () => getCaseTimeline(id!),
    enabled: Boolean(id),
    retry: false,
  });


  async function handleConfirmCancel() {
    if (!id) return;

    setCancelling(true);

    try {
      await changeCaseStatus(
        id,
        "CANCELLED",
        "Cancelled by patient.",
      );

      showToast("Case cancelled.", "success");

      queryClient.invalidateQueries({
        queryKey: ["case", id],
      });

      queryClient.invalidateQueries({
        queryKey: ["case-timeline", id],
      });

      queryClient.invalidateQueries({
        queryKey: ["cases"],
      });

      setConfirmCancelOpen(false);
    } catch (err) {
      showToast(extractErrorMessage(err), "error");
    } finally {
      setCancelling(false);
    }
  }


  if (caseQuery.isLoading) {
    return (
      <AppShell>
        <SkeletonCard />
      </AppShell>
    );
  }


  if (caseQuery.isError || !caseQuery.data) {
    return (
      <AppShell>
        <ErrorState
          message="This case could not be found, or you don't have permission to view it."
          onRetry={() => navigate("/cases")}
        />
      </AppShell>
    );
  }


  const caseData = caseQuery.data;

  const canCancel = CANCELLABLE_STATUSES.has(
    caseData.status,
  );


  return (
    <AppShell>
      <PageHeader
        title={`${TRANSPLANT_TYPE_LABELS[caseData.transplant_type] ?? caseData.transplant_type} Transplant Case`}
        breadcrumbs={[
          {
            label: "Overview",
            to: "/dashboard",
          },
          {
            label: "My Cases",
            to: "/cases",
          },
          {
            label: "Case Details",
          },
        ]}
        actions={
          canCancel ? (
            <Button
              variant="danger"
              size="sm"
              onClick={() => setConfirmCancelOpen(true)}
            >
              Cancel Case
            </Button>
          ) : undefined
        }
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Main case information */}
        <div className="lg:col-span-2 space-y-6">

          <Card>
            <CardHeader className="flex items-center justify-between">
              <h2 className="text-sm font-semibold text-slate-900">
                Case Overview
              </h2>

              <StatusBadge status={caseData.status} />
            </CardHeader>

            <CardBody>
              <dl className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-4 text-sm">

                <div>
                  <dt className="text-slate-500">
                    Transplant Type
                  </dt>

                  <dd className="mt-0.5 font-medium text-slate-900">
                    {
                      TRANSPLANT_TYPE_LABELS[
                        caseData.transplant_type
                      ] ?? caseData.transplant_type
                    }
                  </dd>
                </div>


                <div>
                  <dt className="text-slate-500">
                    Location
                  </dt>

                  <dd className="mt-0.5 font-medium text-slate-900">
                    {[
                      caseData.location_city,
                      caseData.location_state,
                    ]
                      .filter(Boolean)
                      .join(", ") || "Not specified"}
                  </dd>
                </div>


                <div>
                  <dt className="text-slate-500">
                    Preferred Region
                  </dt>

                  <dd className="mt-0.5 font-medium text-slate-900">
                    {caseData.preferred_region ||
                      "Not specified"}
                  </dd>
                </div>


                <div>
                  <dt className="text-slate-500">
                    Required Services
                  </dt>

                  <dd className="mt-0.5 font-medium text-slate-900">
                    {caseData.required_services?.length
                      ? caseData.required_services.join(", ")
                      : "Not specified"}
                  </dd>
                </div>


                <div>
                  <dt className="text-slate-500">
                    Created
                  </dt>

                  <dd className="mt-0.5 font-medium text-slate-900">
                    {formatDateTime(caseData.created_at)}
                  </dd>
                </div>


                <div>
                  <dt className="text-slate-500">
                    Last Updated
                  </dt>

                  <dd className="mt-0.5 font-medium text-slate-900">
                    {formatDateTime(caseData.updated_at)}
                  </dd>
                </div>


                {caseData.case_description && (
                  <div className="sm:col-span-2">
                    <dt className="text-slate-500">
                      Description
                    </dt>

                    <dd className="mt-0.5 text-slate-800">
                      {caseData.case_description}
                    </dd>
                  </div>
                )}

              </dl>
            </CardBody>
          </Card>


          {/* Explainable recommendation entry point */}
          <Card>
            <CardHeader>
              <h2 className="text-sm font-semibold text-slate-900">
                AI-Assisted Centre Recommendations
              </h2>
            </CardHeader>

            <CardBody>
              <p className="text-sm text-slate-500">
                View explainable, non-clinical centre navigation
                recommendations based on verified centre data and
                the information provided in this case.
                Recommendations are intended to support navigation
                and remain subject to verification and human review.
              </p>

              <div className="mt-4">
                <Link
                  to={`/cases/${caseData.id}/recommendations`}
                >
                  <Button variant="primary">
                    View Centre Recommendations
                  </Button>
                </Link>
              </div>
            </CardBody>
          </Card>

        </div>


        {/* Timeline */}
        <div className="space-y-6">

          <Card>
            <CardHeader>
              <h2 className="text-sm font-semibold text-slate-900">
                Timeline
              </h2>
            </CardHeader>

            <CardBody>

              {timelineQuery.isLoading && (
                <p className="text-sm text-slate-400">
                  Loading timeline…
                </p>
              )}


              {timelineQuery.isError && (
                <p className="text-sm text-red-600">
                  Unable to load timeline.
                </p>
              )}


              {timelineQuery.data && (
                <ol className="space-y-4">

                  {timelineQuery.data.map(
                    (entry, idx) => {
                      const meta =
                        STATUS_META[
                          entry.to_status as CaseStatus
                        ];

                      return (
                        <li
                          key={entry.id}
                          className="flex gap-3"
                        >

                          <div className="flex flex-col items-center">
                            <span
                              className={`h-2.5 w-2.5 rounded-full mt-1 ${
                                meta?.dotClasses ??
                                "bg-slate-400"
                              }`}
                            />

                            {idx <
                              timelineQuery.data!.length - 1 && (
                              <span className="w-px flex-1 bg-slate-200 mt-1" />
                            )}
                          </div>


                          <div className="pb-1">
                            <p className="text-sm font-medium text-slate-900">
                              {meta?.label ??
                                entry.to_status}
                            </p>

                            <p className="text-xs text-slate-500 mt-0.5">
                              {formatDateTime(
                                entry.created_at,
                              )}
                            </p>

                            {entry.reason && (
                              <p className="text-xs text-slate-500 mt-1 italic">
                                "{entry.reason}"
                              </p>
                            )}
                          </div>

                        </li>
                      );
                    },
                  )}

                </ol>
              )}

            </CardBody>
          </Card>


          <Link
            to="/cases"
            className="block text-sm text-brand-600 hover:text-brand-700 font-medium text-center"
          >
            ← Back to My Cases
          </Link>

        </div>

      </div>


      <ConfirmDialog
        open={confirmCancelOpen}
        title="Cancel this case?"
        description="This action cannot be undone. You'll need to create a new case if you change your mind."
        confirmLabel="Yes, cancel case"
        cancelLabel="Keep case"
        danger
        isLoading={cancelling}
        onConfirm={handleConfirmCancel}
        onCancel={() => setConfirmCancelOpen(false)}
      />

    </AppShell>
  );
}