export type CaseStatus =
  | "NEW"
  | "DOCUMENT_COLLECTION"
  | "UNDER_REVIEW"
  | "COORDINATOR_REVIEW"
  | "CENTRE_REVIEW"
  | "COMPLETED"
  | "CANCELLED";

interface StatusMeta {
  label: string;
  badgeClasses: string;
  dotClasses: string;
}

export const STATUS_META: Record<CaseStatus, StatusMeta> = {
  NEW: {
    label: "New",
    badgeClasses: "bg-slate-100 text-slate-700 border-slate-200",
    dotClasses: "bg-slate-400",
  },
  DOCUMENT_COLLECTION: {
    label: "Document Collection",
    badgeClasses: "bg-amber-50 text-amber-800 border-amber-200",
    dotClasses: "bg-amber-500",
  },
  UNDER_REVIEW: {
    label: "Under Review",
    badgeClasses: "bg-blue-50 text-blue-800 border-blue-200",
    dotClasses: "bg-blue-500",
  },
  COORDINATOR_REVIEW: {
    label: "Coordinator Review",
    badgeClasses: "bg-indigo-50 text-indigo-800 border-indigo-200",
    dotClasses: "bg-indigo-500",
  },
  CENTRE_REVIEW: {
    label: "Centre Review",
    badgeClasses: "bg-purple-50 text-purple-800 border-purple-200",
    dotClasses: "bg-purple-500",
  },
  COMPLETED: {
    label: "Completed",
    badgeClasses: "bg-green-50 text-green-800 border-green-200",
    dotClasses: "bg-green-500",
  },
  CANCELLED: {
    label: "Cancelled",
    badgeClasses: "bg-red-50 text-red-700 border-red-200",
    dotClasses: "bg-red-400",
  },
};

export const CASE_LIFECYCLE_ORDER: CaseStatus[] = [
  "NEW",
  "DOCUMENT_COLLECTION",
  "UNDER_REVIEW",
  "COORDINATOR_REVIEW",
  "CENTRE_REVIEW",
  "COMPLETED",
];

export const TRANSPLANT_TYPE_LABELS: Record<string, string> = {
  KIDNEY: "Kidney",
  LIVER: "Liver",
  HEART: "Heart",
  LUNG: "Lung",
  CORNEAL: "Corneal",
  BONE_MARROW: "Bone Marrow",
};
