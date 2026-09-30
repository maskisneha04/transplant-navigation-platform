import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import AppShell from "../components/layout/AppShell";
import PageHeader from "../components/ui/PageHeader";
import Card, { CardBody, CardHeader } from "../components/ui/Card";
import Button from "../components/ui/Button";
import Input from "../components/ui/Input";
import Select from "../components/ui/Select";
import { useToast } from "../components/ui/Toast";
import { createCase } from "../services/caseService";
import { extractErrorMessage } from "../services/authService";
import { TRANSPLANT_TYPE_LABELS } from "../constants/status";

const TRANSPLANT_TYPE_OPTIONS = Object.entries(TRANSPLANT_TYPE_LABELS).map(([value, label]) => ({ value, label }));

const TRAVEL_PREFERENCE_OPTIONS = [
  { value: "short_distance", label: "Prefer short travel distance" },
  { value: "any_distance", label: "Willing to travel any distance" },
  { value: "region_specific", label: "Prefer a specific region" },
];

export default function CaseNewPage() {
  const navigate = useNavigate();
  const { showToast } = useToast();

  const [transplantType, setTransplantType] = useState("");
  const [city, setCity] = useState("");
  const [state, setState] = useState("");
  const [preferredRegion, setPreferredRegion] = useState("");
  const [travelPreference, setTravelPreference] = useState("");
  const [requiredServices, setRequiredServices] = useState("");
  const [description, setDescription] = useState("");

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  function validate(): boolean {
    const next: Record<string, string> = {};
    if (!transplantType) next.transplantType = "Please select a transplant type.";
    setErrors(next);
    return Object.keys(next).length === 0;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setSubmitError(null);
    if (!validate()) return;

    setSubmitting(true);
    try {
      const created = await createCase({
        transplant_type: transplantType,
        location_city: city || undefined,
        location_state: state || undefined,
        preferred_region: preferredRegion || undefined,
        required_services: requiredServices
          ? requiredServices.split(",").map((s) => s.trim()).filter(Boolean)
          : undefined,
        case_description: description || undefined,
        preferences: travelPreference
          ? [{ preference_key: "travel", preference_value: travelPreference }]
          : undefined,
      });
      showToast("Case created successfully.", "success");
      navigate(`/cases/${created.id}`);
    } catch (err) {
      setSubmitError(extractErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <AppShell>
      <PageHeader
        title="Create a New Case"
        description="This information helps coordinators understand your situation. No medical diagnosis or eligibility questions are asked here."
        breadcrumbs={[{ label: "Overview", to: "/dashboard" }, { label: "My Cases", to: "/cases" }, { label: "New Case" }]}
      />

      <form onSubmit={handleSubmit} className="space-y-6 max-w-2xl">
        <Card>
          <CardHeader>
            <h2 className="text-sm font-semibold text-slate-900">Transplant Information</h2>
          </CardHeader>
          <CardBody className="space-y-4">
            <Select
              label="Transplant Type"
              required
              value={transplantType}
              onChange={(e) => setTransplantType(e.target.value)}
              options={TRANSPLANT_TYPE_OPTIONS}
              placeholder="Select a transplant type"
              error={errors.transplantType}
            />
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5" htmlFor="description">
                Case Description <span className="text-slate-400 font-normal">(optional)</span>
              </label>
              <textarea
                id="description"
                rows={3}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                maxLength={2000}
                placeholder="Any administrative context that would help a coordinator (not a medical history)"
                className="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent"
              />
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <h2 className="text-sm font-semibold text-slate-900">Location</h2>
          </CardHeader>
          <CardBody className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Input label="City" value={city} onChange={(e) => setCity(e.target.value)} placeholder="e.g. Bengaluru" />
              <Input label="State" value={state} onChange={(e) => setState(e.target.value)} placeholder="e.g. Karnataka" />
            </div>
            <Input
              label="Preferred Region"
              value={preferredRegion}
              onChange={(e) => setPreferredRegion(e.target.value)}
              placeholder="e.g. South India"
              helpText="A broader region you'd consider if a suitable local option isn't available."
            />
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <h2 className="text-sm font-semibold text-slate-900">Preferences</h2>
          </CardHeader>
          <CardBody className="space-y-4">
            <Select
              label="Travel Preference"
              value={travelPreference}
              onChange={(e) => setTravelPreference(e.target.value)}
              options={TRAVEL_PREFERENCE_OPTIONS}
              placeholder="Select a travel preference"
            />
            <Input
              label="Required Services"
              value={requiredServices}
              onChange={(e) => setRequiredServices(e.target.value)}
              placeholder="e.g. Kidney transplant support, Post-op care"
              helpText="Comma-separated list of services you're looking for."
            />
          </CardBody>
        </Card>

        {submitError && (
          <div className="rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm px-4 py-3">{submitError}</div>
        )}

        <div className="flex items-center justify-end gap-3">
          <Button type="button" variant="secondary" onClick={() => navigate("/cases")} disabled={submitting}>
            Cancel
          </Button>
          <Button type="submit" isLoading={submitting}>
            Create Case
          </Button>
        </div>
      </form>
    </AppShell>
  );
}
