import { useState } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";

import AppShell from "../components/layout/AppShell";
import PageHeader from "../components/ui/PageHeader";
import Card from "../components/ui/Card";
import Input from "../components/ui/Input";
import Select from "../components/ui/Select";
import Button from "../components/ui/Button";
import EmptyState from "../components/ui/EmptyState";
import ErrorState from "../components/ui/ErrorState";
import { SkeletonTableRows } from "../components/ui/Skeleton";

import { listCentres } from "../services/centreService";
import type { CentreFilters } from "../types/centre";

const STATE_OPTIONS = [
  "Andhra Pradesh",
  "Arunachal Pradesh",
  "Assam",
  "Bihar",
  "Chhattisgarh",
  "Delhi",
  "Goa",
  "Gujarat",
  "Haryana",
  "Himachal Pradesh",
  "Jharkhand",
  "Karnataka",
  "Kerala",
  "Madhya Pradesh",
  "Maharashtra",
  "Manipur",
  "Meghalaya",
  "Mizoram",
  "Nagaland",
  "Odisha",
  "Punjab",
  "Rajasthan",
  "Sikkim",
  "Tamil Nadu",
  "Telangana",
  "Tripura",
  "Uttar Pradesh",
  "Uttarakhand",
  "West Bengal",
];

const TRANSPLANT_TYPE_OPTIONS = [
  "Kidney",
  "Liver",
  "Heart",
  "Lung",
  "Pancreas",
  "Intestine",
  "Cornea",
  "Bone",
  "Skin",
];

const REGISTRATION_TYPE_OPTIONS = [
  "Transplant Centre",
  "Retrieval Centre",
];

const PAGE_SIZE = 20;

export default function CentreListPage() {
  const [search, setSearch] = useState("");
  const [state, setState] = useState("");
  const [transplantType, setTransplantType] = useState("");
  const [registrationType, setRegistrationType] = useState("");
  const [skip, setSkip] = useState(0);

  const filters: CentreFilters = {
    search: search.trim() || undefined,
    state: state || undefined,
    transplant_type: transplantType || undefined,
    registration_type: registrationType || undefined,
    skip,
    limit: PAGE_SIZE,
  };

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["centres", filters],
    queryFn: () => listCentres(filters),
  });

  function clearFilters() {
    setSearch("");
    setState("");
    setTransplantType("");
    setRegistrationType("");
    setSkip(0);
  }

  function handleSearchChange(value: string) {
    setSearch(value);
    setSkip(0);
  }

  function handleStateChange(value: string) {
    setState(value);
    setSkip(0);
  }

  function handleTransplantTypeChange(value: string) {
    setTransplantType(value);
    setSkip(0);
  }

  function handleRegistrationTypeChange(value: string) {
    setRegistrationType(value);
    setSkip(0);
  }

  const centres = data ?? [];
  const hasNextPage = centres.length === PAGE_SIZE;
  const hasPreviousPage = skip > 0;

  return (
    <AppShell>
      <PageHeader
        title="Transplant Centres"
        description="Browse NOTTO-sourced transplant and retrieval centres."
        breadcrumbs={[
          { label: "Overview", to: "/dashboard" },
          { label: "Transplant Centres" },
        ]}
      />

      <Card className="mb-6">
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Input
            label="Search"
            placeholder="Search centre name"
            value={search}
            onChange={(event) =>
              handleSearchChange(event.target.value)
            }
          />

          <Select
            label="State"
            value={state}
            onChange={(event) =>
              handleStateChange(event.target.value)
            }
            placeholder="All states"
            options={STATE_OPTIONS.map((value) => ({
              value,
              label: value,
            }))}
          />

          <Select
            label="Transplant type"
            value={transplantType}
            onChange={(event) =>
              handleTransplantTypeChange(event.target.value)
            }
            placeholder="All transplant types"
            options={TRANSPLANT_TYPE_OPTIONS.map((value) => ({
              value,
              label: value,
            }))}
          />

          <Select
            label="Registration type"
            value={registrationType}
            onChange={(event) =>
              handleRegistrationTypeChange(event.target.value)
            }
            placeholder="All registration types"
            options={REGISTRATION_TYPE_OPTIONS.map((value) => ({
              value,
              label: value,
            }))}
          />
        </div>

        <div className="mt-4 flex justify-end">
          <Button variant="secondary" onClick={clearFilters}>
            Clear filters
          </Button>
        </div>
      </Card>

      <Card className="overflow-hidden">
        {isLoading ? (
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <tbody>
                <SkeletonTableRows rows={8} />
              </tbody>
            </table>
          </div>
        ) : isError ? (
          <ErrorState
  message="Unable to load transplant centres. Please try again."
  onRetry={() => refetch()}
/>
        ) : centres.length === 0 ? (
          <EmptyState
            title="No transplant centres found"
            description="Try changing or clearing your filters."
            action={
              <Button variant="secondary" onClick={clearFilters}>
                Clear filters
              </Button>
            }
          />
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="min-w-full text-left text-sm">
                <thead className="border-b border-slate-200 bg-slate-50">
                  <tr>
                    <th className="px-6 py-3 font-semibold text-slate-700">
                      Centre
                    </th>
                    <th className="px-6 py-3 font-semibold text-slate-700">
                      Location
                    </th>
                    <th className="px-6 py-3 font-semibold text-slate-700">
                      Registration
                    </th>
                    <th className="px-6 py-3 font-semibold text-slate-700">
                      Transplant / Tissue Types
                    </th>
                    <th className="px-6 py-3 font-semibold text-slate-700">
                      Source
                    </th>
                  </tr>
                </thead>

                <tbody className="divide-y divide-slate-100">
                  {centres.map((centre) => (
                    <tr
                      key={centre.id}
                      className="hover:bg-slate-50"
                    >
                      <td className="px-6 py-4">
                        <Link
                          to={`/centres/${centre.id}`}
                          className="font-medium text-brand-600 hover:text-brand-700"
                        >
                          {centre.name}
                        </Link>
                      </td>

                      <td className="px-6 py-4 text-slate-600">
                        {centre.city || centre.district
                          ? [centre.city, centre.district, centre.state]
                              .filter(Boolean)
                              .join(", ")
                          : centre.state || "—"}
                      </td>

                      <td className="px-6 py-4 text-slate-600">
                        {centre.registration_type || "—"}
                      </td>

                      <td className="px-6 py-4 text-slate-600">
                        {centre.transplant_types?.length
                          ? centre.transplant_types.join(", ")
                          : "—"}
                      </td>

                      <td className="px-6 py-4">
                        <span className="inline-flex rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-700">
                          {centre.data_source || "Unknown"}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="flex items-center justify-between border-t border-slate-200 px-6 py-4">
              <p className="text-sm text-slate-500">
                Showing {skip + 1}–{skip + centres.length}
              </p>

              <div className="flex gap-2">
                <Button
                  variant="secondary"
                  disabled={!hasPreviousPage}
                  onClick={() =>
                    setSkip(Math.max(0, skip - PAGE_SIZE))
                  }
                >
                  Previous
                </Button>

                <Button
                  variant="secondary"
                  disabled={!hasNextPage}
                  onClick={() =>
                    setSkip(skip + PAGE_SIZE)
                  }
                >
                  Next
                </Button>
              </div>
            </div>
          </>
        )}
      </Card>
    </AppShell>
  );
}