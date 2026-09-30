import { STATUS_META, type CaseStatus } from "../../constants/status";

export default function StatusBadge({ status }: { status: string }) {
  const meta = STATUS_META[status as CaseStatus] ?? {
    label: status,
    badgeClasses: "bg-slate-100 text-slate-700 border-slate-200",
    dotClasses: "bg-slate-400",
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium ${meta.badgeClasses}`}
      role="status"
    >
      <span className={`h-1.5 w-1.5 rounded-full ${meta.dotClasses}`} aria-hidden="true" />
      {meta.label}
    </span>
  );
}
