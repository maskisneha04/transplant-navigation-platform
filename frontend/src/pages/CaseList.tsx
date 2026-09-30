import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import AppShell from "../components/layout/AppShell";
import PageHeader from "../components/ui/PageHeader";
import Card from "../components/ui/Card";
import Button from "../components/ui/Button";
import StatusBadge from "../components/ui/StatusBadge";
import EmptyState from "../components/ui/EmptyState";
import ErrorState from "../components/ui/ErrorState";
import { SkeletonTableRows } from "../components/ui/Skeleton";
import { listCases } from "../services/caseService";
import { TRANSPLANT_TYPE_LABELS } from "../constants/status";

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
}

export default function CaseListPage() {
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["cases"],
    queryFn: listCases,
  });

  return (
    <AppShell>
      <PageHeader
        title="My Cases"
        description="Track and manage your transplant coordination cases."
        breadcrumbs={[{ label: "Overview", to: "/dashboard" }, { label: "My Cases" }]}
        actions={
          <Link to="/cases/new">
            <Button>+ New Case</Button>
          </Link>
        }
      />

      <Card className="overflow-hidden">
        {isLoading && <SkeletonTableRows rows={4} />}

        {isError && <ErrorState message="Unable to load your cases. Please try again." onRetry={() => refetch()} />}

        {!isLoading && !isError && data && data.length === 0 && (
          <EmptyState
            title="No cases yet"
            description="Create your first transplant coordination case to get started."
            action={
              <Link to="/cases/new">
                <Button size="sm">+ New Case</Button>
              </Link>
            }
          />
        )}

        {!isLoading && !isError && data && data.length > 0 && (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-100 text-left text-xs font-medium text-slate-500 uppercase tracking-wide">
                  <th className="px-6 py-3">Transplant Type</th>
                  <th className="px-6 py-3">Location</th>
                  <th className="px-6 py-3">Status</th>
                  <th className="px-6 py-3">Created</th>
                  <th className="px-6 py-3">Last Updated</th>
                  <th className="px-6 py-3 sr-only">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {data.map((c) => (
                  <tr key={c.id} className="hover:bg-slate-50">
                    <td className="px-6 py-4 font-medium text-slate-900">
                      {TRANSPLANT_TYPE_LABELS[c.transplant_type] ?? c.transplant_type}
                    </td>
                    <td className="px-6 py-4 text-slate-600">
                      {[c.location_city, c.location_state].filter(Boolean).join(", ") || "—"}
                    </td>
                    <td className="px-6 py-4">
                      <StatusBadge status={c.status} />
                    </td>
                    <td className="px-6 py-4 text-slate-500">{formatDate(c.created_at)}</td>
                    <td className="px-6 py-4 text-slate-500">{formatDate(c.updated_at)}</td>
                    <td className="px-6 py-4 text-right">
                      <Link to={`/cases/${c.id}`} className="text-brand-600 hover:text-brand-700 font-medium">
                        View
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </AppShell>
  );
}
