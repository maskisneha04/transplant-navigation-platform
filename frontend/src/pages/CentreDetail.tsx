import { useNavigate, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";

import AppShell from "../components/layout/AppShell";
import PageHeader from "../components/ui/PageHeader";
import Card, { CardBody, CardHeader } from "../components/ui/Card";
import Button from "../components/ui/Button";
import ErrorState from "../components/ui/ErrorState";
import { SkeletonCard } from "../components/ui/Skeleton";

import { getCentre } from "../services/centreService";

function formatDateTime(value: string | null) {
  if (!value) return "Not available";

  return new Date(value).toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function CentreDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const centreQuery = useQuery({
    queryKey: ["centre", id],
    queryFn: () => getCentre(id!),
    enabled: Boolean(id),
    retry: false,
  });

  if (centreQuery.isLoading) {
    return (
      <AppShell>
        <SkeletonCard />
      </AppShell>
    );
  }

  if (centreQuery.isError || !centreQuery.data) {
    return (
      <AppShell>
        <ErrorState
          message="This transplant centre could not be found."
          onRetry={() => navigate("/centres")}
        />
      </AppShell>
    );
  }

  const centre = centreQuery.data;

  return (
    <AppShell>
      <PageHeader
        title={centre.name}
        description="Transplant centre information and source provenance."
        breadcrumbs={[
          { label: "Overview", to: "/dashboard" },
          { label: "Transplant Centres", to: "/centres" },
          { label: centre.name },
        ]}
      />

      <div className="mb-6">
        <Button
          variant="secondary"
          onClick={() => navigate("/centres")}
        >
          ← Back to centres
        </Button>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader title="Centre information" />
          <CardBody>
            <dl className="space-y-4">
              <div>
                <dt className="text-sm font-medium text-slate-500">
                  Address
                </dt>
                <dd className="mt-1 text-slate-900">
                  {centre.address || "Not available"}
                </dd>
              </div>

              <div>
                <dt className="text-sm font-medium text-slate-500">
                  Location
                </dt>
                <dd className="mt-1 text-slate-900">
                  {[
                    centre.city,
                    centre.district,
                    centre.state,
                  ]
                    .filter(Boolean)
                    .join(", ") || "Not available"}
                </dd>
              </div>

              <div>
                <dt className="text-sm font-medium text-slate-500">
                  Registration type
                </dt>
                <dd className="mt-1 text-slate-900">
                  {centre.registration_type || "Not available"}
                </dd>
              </div>

              <div>
                <dt className="text-sm font-medium text-slate-500">
                  Transplant / tissue types
                </dt>
                <dd className="mt-1 text-slate-900">
                  {centre.transplant_types?.length
                    ? centre.transplant_types.join(", ")
                    : "Not available"}
                </dd>
              </div>

              {centre.website && (
                <div>
                  <dt className="text-sm font-medium text-slate-500">
                    Website
                  </dt>
                  <dd className="mt-1">
                    <a
                      href={centre.website}
                      target="_blank"
                      rel="noreferrer"
                      className="text-brand-600 hover:text-brand-700"
                    >
                      Visit centre website
                    </a>
                  </dd>
                </div>
              )}
            </dl>
          </CardBody>
        </Card>

        <Card>
          <CardHeader title="Source and verification" />
          <CardBody>
            <dl className="space-y-4">
              <div>
                <dt className="text-sm font-medium text-slate-500">
                  Data source
                </dt>
                <dd className="mt-1 text-slate-900">
                  {centre.data_source || "Not available"}
                </dd>
              </div>

              <div>
                <dt className="text-sm font-medium text-slate-500">
                  Verification status
                </dt>
                <dd className="mt-1 text-slate-900">
                  {centre.verification_status}
                </dd>
              </div>

              <div>
                <dt className="text-sm font-medium text-slate-500">
                  Source record ID
                </dt>
                <dd className="mt-1 text-slate-900">
                  {centre.source_record_id ?? "Not available"}
                </dd>
              </div>

              <div>
                <dt className="text-sm font-medium text-slate-500">
                  Dataset version
                </dt>
                <dd className="mt-1 text-slate-900">
                  {centre.source_dataset_version || "Not available"}
                </dd>
              </div>

              <div>
                <dt className="text-sm font-medium text-slate-500">
                  Last verified
                </dt>
                <dd className="mt-1 text-slate-900">
                  {formatDateTime(centre.last_verified_at)}
                </dd>
              </div>
            </dl>
          </CardBody>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader title="Additional details" />
          <CardBody>
            <p className="whitespace-pre-wrap text-sm leading-6 text-slate-700">
              {centre.details || "No additional details available."}
            </p>
          </CardBody>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader title="Navigation and recommendation" />
          <CardBody>
            <p className="text-sm leading-6 text-slate-600">
              Explainable centre recommendation will be available in the
              next module. Recommendations will use documented,
              non-clinical navigation factors and will remain subject to
              human review.
            </p>
          </CardBody>
        </Card>
      </div>
    </AppShell>
  );
}