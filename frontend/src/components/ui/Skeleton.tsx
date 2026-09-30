export function SkeletonLine({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse bg-slate-200 rounded ${className}`} />;
}

export function SkeletonCard() {
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6 space-y-3">
      <SkeletonLine className="h-4 w-1/3" />
      <SkeletonLine className="h-3 w-2/3" />
      <SkeletonLine className="h-3 w-1/2" />
    </div>
  );
}

export function SkeletonTableRows({ rows = 4 }: { rows?: number }) {
  return (
    <div className="divide-y divide-slate-100">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex items-center gap-4 px-6 py-4">
          <SkeletonLine className="h-4 w-24" />
          <SkeletonLine className="h-4 w-20" />
          <SkeletonLine className="h-4 flex-1" />
          <SkeletonLine className="h-4 w-16" />
        </div>
      ))}
    </div>
  );
}
