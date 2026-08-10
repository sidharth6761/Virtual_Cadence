import { Sidebar } from '../components/layout/Sidebar';
import { TopBar } from '../components/layout/TopBar';
import { ProjectUploadForm } from '../components/upload/ProjectUploadForm';

export function DashboardPage() {
  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(59,130,246,0.08),_transparent_32%),linear-gradient(135deg,_#f8fafc_0%,_#f1f5f9_100%)] text-slate-900 dark:bg-[radial-gradient(circle_at_top_left,_rgba(59,130,246,0.18),_transparent_32%),linear-gradient(135deg,_#020617_0%,_#0f172a_100%)] dark:text-slate-100">
      <div className="mx-auto flex min-h-screen max-w-7xl flex-col lg:flex-row">
        <Sidebar />
        <div className="flex-1">
          <TopBar />
          <main className="px-4 py-6 sm:px-6 lg:px-8 lg:py-8">
            <section className="rounded-[32px] border border-slate-200 bg-white/80 p-6 shadow-[0_20px_70px_-35px_rgba(15,23,42,0.35)] backdrop-blur dark:border-slate-800 dark:bg-slate-950/80">
              <div className="mb-8 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
                <div>
                  <p className="text-sm font-medium uppercase tracking-[0.24em] text-blue-600">Upload workspace</p>
                  <h2 className="mt-2 text-2xl font-semibold text-slate-900 dark:text-slate-100">Design your next synthesis job</h2>
                  <p className="mt-2 max-w-2xl text-sm text-slate-600 dark:text-slate-400">
                    Add the design files, constraints, and library assets needed for Cadence Genus synthesis. The backend stores everything locally for now and is ready for future remote execution.
                  </p>
                </div>
                <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-600 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-300">
                  <p className="font-medium text-slate-900 dark:text-slate-100">Local mode</p>
                  <p className="mt-1">No SSH or lab worker yet</p>
                </div>
              </div>

              <ProjectUploadForm />
            </section>
          </main>
        </div>
      </div>
    </div>
  );
}
