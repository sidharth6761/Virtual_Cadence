import { useCallback, useEffect, useState } from 'react';
import { supabase } from '../../supabase/client';

interface JobRow {
  id: number;
  project_id: number;
  status: string;
  created_at: string;
}

function formatDate(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString();
}

function statusClass(status: string): string {
  const s = status.toLowerCase();
  if (s === 'queued' || s === 'completed') return 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/50 dark:text-emerald-300';
  if (s === 'running' || s === 'uploading') return 'bg-amber-100 text-amber-700 dark:bg-amber-900/50 dark:text-amber-300';
  if (s === 'failed' || s === 'cancelled') return 'bg-red-100 text-red-700 dark:bg-red-900/50 dark:text-red-300';
  return 'bg-slate-200 text-slate-600 dark:bg-slate-800 dark:text-slate-300';
}

export function JobsList() {
  const [jobs, setJobs] = useState<JobRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadJobs = useCallback(async () => {
    setError(null);
    const { data, error: err } = await supabase
      .from('jobs')
      .select('id, project_id, status, created_at')
      .order('created_at', { ascending: false })
      .limit(20);
    if (err) {
      setError(err.message);
    } else {
      setJobs((data as JobRow[]) ?? []);
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- initial data load
    void loadJobs();
  }, [loadJobs]);

  return (
    <div className="rounded-3xl border border-slate-200 bg-white/80 p-6 shadow-sm dark:border-slate-800 dark:bg-slate-950/80">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">Uploaded jobs</h3>
          <p className="text-sm text-slate-500 dark:text-slate-400">Recent synthesis submissions stored in Supabase.</p>
        </div>
        <button
          type="button"
          onClick={() => {
            setLoading(true);
            void loadJobs();
          }}
          className="rounded-2xl border border-slate-300 px-3 py-1.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-900"
        >
          Refresh
        </button>
      </div>

      {loading ? (
        <p className="py-6 text-sm text-slate-500">Loading jobs…</p>
      ) : error ? (
        <p className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-800 dark:bg-red-950 dark:text-red-300">
          {error}
        </p>
      ) : jobs.length === 0 ? (
        <p className="py-6 text-sm text-slate-500">No jobs yet. Submit an upload to see it here.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-slate-500 dark:border-slate-800">
                <th className="py-2 pr-4 font-medium">Job</th>
                <th className="py-2 pr-4 font-medium">Status</th>
                <th className="py-2 font-medium">Created</th>
              </tr>
            </thead>
            <tbody>
              {jobs.map((job) => (
                <tr key={job.id} className="border-b border-slate-100 dark:border-slate-800/60">
                  <td className="py-2.5 pr-4 font-medium text-slate-900 dark:text-slate-100">JOB_{String(job.id).padStart(4, '0')}</td>
                  <td className="py-2.5 pr-4">
                    <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${statusClass(job.status)}`}>{job.status}</span>
                  </td>
                  <td className="py-2.5 text-slate-600 dark:text-slate-300">{formatDate(job.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}