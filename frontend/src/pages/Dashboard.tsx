import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import AppShell from "../components/layout/AppShell";
import PageHeader from "../components/ui/PageHeader";
import Card, { CardBody } from "../components/ui/Card";
import Button from "../components/ui/Button";
import StatusBadge from "../components/ui/StatusBadge";
import { SkeletonCard } from "../components/ui/Skeleton";
import { listCases } from "../services/caseService";
import { me } from "../services/authService";
import type { AuthUser } from "../types/auth";
import { TRANSPLANT_TYPE_LABELS } from "../constants/status";

const ACTIVE_STATUSES = new Set(["NEW", "DOCUMENT_COLLECTION", "UNDER_REVIEW", "COORDINATOR_REVIEW", "CENTRE_REVIEW"]);

export default function DashboardPage() {
  const [user, setUser] = useState<AuthUser | null>(null);

  useEffect(() => {
    me().then(setUser).catch(() => {});
  }, []);

  const { data: cases, isLoading } = useQuery({
    queryKey: ["cases"],
    queryFn: listCases,
  });

  const activeCases = cases?.filter((c) => ACTIVE_STATUSES.has(c.status)) ?? [];
  const mostRecent = cases?.[0];

  return (
    <AppShell>
      <PageHeader
        title={user ? `Welcome back${user.email ? "" : ""}` : "Welcome"}
        description="Here's an overview of your transplant coordination activity."
      />

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <Card>
          <CardBody>
            <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">Active Cases</p>
            <p className="mt-2 text-2xl font-semibold text-slate-900">
              {isLoading ? "—" : activeCases.length}
            </p>
          </CardBody>
        </Card>
        <Card>
          <CardBody>
            <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">Current Case Status</p>
            <div className="mt-2">
              {isLoading ? (
                <span className="text-2xl text-slate-300">—</span>
              ) : mostRecent ? (
                <StatusBadge status={mostRecent.status} />
              ) : (
                <span className="text-sm text-slate-400">No active cases</span>
              )}
            </div>
          </CardBody>
        </Card>
        <Card>
          <CardBody>
            <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">Total Cases</p>
            <p className="mt-2 text-2xl font-semibold text-slate-900">
              {isLoading ? "—" : cases?.length ?? 0}
            </p>
          </CardBody>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card>
            <CardBody>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-sm font-semibold text-slate-900">Recent Activity</h2>
                <Link to="/cases" className="text-xs text-brand-600 hover:text-brand-700 font-medium">
                  View all
                </Link>
              </div>

              {isLoading && <SkeletonCard />}

              {!isLoading && (!cases || cases.length === 0) && (
                <p className="text-sm text-slate-500 py-6 text-center">
                  No active cases. Create your first case to get started.
                </p>
              )}

              {!isLoading && cases && cases.length > 0 && (
                <ul className="divide-y divide-slate-100">
                  {cases.slice(0, 5).map((c) => (
                    <li key={c.id} className="py-3 flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-slate-900">
                          {TRANSPLANT_TYPE_LABELS[c.transplant_type] ?? c.transplant_type} Case
                        </p>
                        <p className="text-xs text-slate-500 mt-0.5">
                          Updated {new Date(c.updated_at).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="flex items-center gap-3">
                        <StatusBadge status={c.status} />
                        <Link to={`/cases/${c.id}`} className="text-xs text-brand-600 hover:text-brand-700 font-medium">
                          View
                        </Link>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </CardBody>
          </Card>
        </div>

        <div>
  <Card>
    <CardBody className="space-y-3">
      <h2 className="text-sm font-semibold text-slate-900 mb-1">
        Quick Actions
      </h2>

      <Link to="/cases/new" className="block">
        <Button className="w-full justify-center">
          + Create New Case
        </Button>
      </Link>

      <Link to="/cases" className="block">
        <Button variant="secondary" className="w-full justify-center">
          View My Cases
        </Button>
      </Link>

      <Link to="/centres" className="block">
        <Button variant="secondary" className="w-full justify-center">
          Browse Transplant Centres
        </Button>
      </Link>
    </CardBody>
  </Card>
</div>
      </div>
    </AppShell>
  );
}
