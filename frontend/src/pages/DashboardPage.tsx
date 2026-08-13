import { TopBar } from '../components/layout/TopBar';
import { ProjectUploadForm } from '../components/upload/ProjectUploadForm';
import { JobsList } from '../components/jobs/JobsList';
import { RecentResults } from '../components/results/RecentResults';

export function DashboardPage() {
  return (
    <div className="min-h-screen bg-slate-50">
      <TopBar />
      <main className="mx-auto max-w-6xl px-6 py-8">
        <section className="mb-10">
          <h2 className="mb-6 text-lg font-semibold text-slate-900">Synthesis Setup</h2>
          <ProjectUploadForm />
        </section>

        <section className="mb-10">
          <h2 className="mb-4 text-lg font-semibold text-slate-900">Active Queue</h2>
          <JobsList />
        </section>

        <section>
          <RecentResults />
        </section>
      </main>
    </div>
  );
}
