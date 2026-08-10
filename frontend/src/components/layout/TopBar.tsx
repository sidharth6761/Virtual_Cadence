export function TopBar() {
  return (
    <header className="flex items-center justify-between border-b border-slate-200 bg-white/80 px-6 py-4 backdrop-blur dark:border-slate-800 dark:bg-slate-950/80">
      <div>
        <p className="text-sm text-slate-500 dark:text-slate-400">Remote EDA Automation</p>
        <h1 className="text-lg font-semibold text-slate-900 dark:text-slate-100">New synthesis project</h1>
      </div>

      <div className="flex items-center gap-3">
        <div className="hidden rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-sm text-slate-600 md:block dark:border-slate-800 dark:bg-slate-900 dark:text-slate-300">
          Local backend ready
        </div>
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-600 font-semibold text-white">
          JD
        </div>
      </div>
    </header>
  );
}
