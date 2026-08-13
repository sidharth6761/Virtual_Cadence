import { useCallback, useEffect, useState } from 'react';
import { supabase } from '../../supabase/client';

interface JobRow {
  id: number;
  project_id: number;
  project_name?: string;
  status: string;
  created_at: string;
  updated_at: string;
}

function formatJobId(id: number): string {
  return `JOB-${String(id).padStart(4, '0')}`;
}

function formatElapsed(createdAt: string): string {
  const start = new Date(createdAt).getTime();
  if (Number.isNaN(start)) return '--:--:--';
  const diff = Math.floor((Date.now() - start) / 1000);
  const h = String(Math.floor(diff / 3600)).padStart(2, '0');
  const m = String(Math.floor((diff % 3600) / 60)).padStart(2, '0');
  const s = String(diff % 60).padStart(2, '0');
  return `${h}:${m}:${s}`;
}

function statusBadge(status: string): { label: string; className: string } {
  const s = status.toLowerCase();
  if (s === 'running')
    return { label: 'Running', className: 'bg-blue-600 text-white' };
  if (s === 'queued')
    return { label: 'Queued', className: 'bg-amber-500 text-white' };
  if (s === 'completed' || s === 'done')
    return { label: 'Done', className: 'bg-emerald-500 text-white' };
  if (s === 'failed')
    return { label: 'Failed', className: 'bg-red-500 text-white' };
  return { label: status, className: 'bg-slate-400 text-white' };
}

function progressPercent(status: string): number {
  const s = status.toLowerCase();
  if (s === 'completed' || s === 'done') return 100;
  if (s === 'running') return 60;
  if (s === 'queued' || s === 'uploading') return 20;
  if (s === 'failed') return 0;
  return 10;
}

function progressBarColor(status: string): string {
  const s = status.toLowerCase();
  if (s === 'completed' || s === 'done') return 'bg-emerald-500';
  if (s === 'running') return 'bg-blue-600';
  if (s === 'queued') return 'bg-slate-300';
  return 'bg-slate-300';
}

export function JobsList() {
  const [jobs, setJobs] = useState<JobRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadJobs = useCallback(async () => {
    setError(null);
    const { data, error: err } = await supabase
      .from('jobs')
      .select('id, project_id, status, created_at, updated_at, projects(name)')
      .order('created_at', { ascending: false })
      .limit(20);
    if (err) {
      setError(err.message);
    } else {
      const rows = ((data as Record<string, unknown>[] | null) ?? []).map((row) => ({
        id: row.id as number,
        project_id: row.project_id as number,
        status: row.status as string,
        created_at: row.created_at as string,
        updated_at: row.updated_at as string,
        project_name: (row.projects as { name: string } | null)?.name ?? 'Untitled',
      }));
      setJobs(rows);
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- initial data load
    void loadJobs();
  }, [loadJobs]);

  return (
    <div className="rounded-xl border border-slate-200 bg-white">
      <div className="flex items-center justify-between border-b border-slate-200 px-5 py-4">
        <p className="text-sm font-medium text-slate-900">Jobs</p>
        <button
          type="button"
          onClick={() => { setLoading(true); void loadJobs(); }}
          className="rounded-lg border border-slate-300 px-3 py-1.5 text-xs font-medium text-slate-700 transition hover:bg-slate-100"
        >
          Refresh
        </button>
      </div>

      {loading ? (
        <p className="px-5 py-6 text-sm text-slate-500">Loading jobs...</p>
      ) : error ? (
        <p className="mx-5 my-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</p>
      ) : jobs.length === 0 ? (
        <p className="px-5 py-6 text-sm text-slate-500">No jobs yet. Submit an upload to see it here.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-slate-100 text-xs uppercase tracking-wider text-slate-500">
                <th className="px-5 py-3 font-medium">Job ID</th>
                <th className="px-5 py-3 font-medium">Project</th>
                <th className="px-5 py-3 font-medium">Status</th>
                <th className="px-5 py-3 font-medium">Progress</th>
                <th className="px-5 py-3 font-medium text-right">Time Elapsed</th>
              </tr>
            </thead>
            <tbody>
              {jobs.map((job) => {
                const badge = statusBadge(job.status);
                const pct = progressPercent(job.status);
                return (
                  <tr key={job.id} className="border-b border-slate-100 last:border-0">
                    <td className="whitespace-nowrap px-5 py-3 font-semibold text-slate-900">{formatJobId(job.id)}</td>
                    <td className="px-5 py-3 text-slate-600">{job.project_name}</td>
                    <td className="px-5 py-3">
                      <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${badge.className}`}>
                        {badge.label}
                      </span>
                    </td>
                    <td className="px-5 py-3">
                      <div className="h-2 w-40 overflow-hidden rounded-full bg-slate-200">
                        <div
                          className={`h-full rounded-full transition-all ${progressBarColor(job.status)}`}
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                    </td>
                    <td className="whitespace-nowrap px-5 py-3 text-right font-mono text-xs text-slate-500">
                      {formatElapsed(job.created_at)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
