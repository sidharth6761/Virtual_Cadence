interface StatCardProps {
  label: string;
  value: string;
  unit: string;
}

function StatCard({ label, value, unit }: StatCardProps) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5">
      <p className="text-xs font-medium uppercase tracking-wider text-slate-500">{label}</p>
      <p className="mt-2 text-2xl font-bold text-slate-900">
        {value}
        <span className="ml-1 text-sm font-normal text-slate-500">{unit}</span>
      </p>
    </div>
  );
}

export function RecentResults() {
  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-slate-900">
          Recent Results{' '}
          <span className="text-sm font-normal text-slate-400">(JOB-9019)</span>
        </h2>
        <button
          type="button"
          className="text-sm font-medium text-blue-600 hover:underline"
        >
          View Full Report
        </button>
      </div>
      <div className="grid gap-4 sm:grid-cols-3">
        <StatCard label="Total Area" value="14,250" unit="μm²" />
        <StatCard label="Critical Path" value="2.45" unit="ns" />
        <StatCard label="Total Power" value="18.5" unit="mW" />
      </div>
    </div>
  );
}
