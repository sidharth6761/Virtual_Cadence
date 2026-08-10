const navItems = [
  { label: 'Dashboard', active: true },
  { label: 'New Job' },
  { label: 'Jobs' },
  { label: 'Reports' },
  { label: 'Settings' },
];

export function Sidebar() {
  return (
    <aside className="hidden w-64 flex-col border-r border-slate-200 bg-white/80 px-6 py-8 backdrop-blur xl:flex dark:border-slate-800 dark:bg-slate-950/80">
      <div className="mb-8">
        <p className="text-sm font-semibold uppercase tracking-[0.25em] text-slate-500">Virtual Cadence</p>
        <h2 className="mt-2 text-xl font-semibold text-slate-900 dark:text-slate-100">EDA Automation</h2>
      </div>

      <nav className="space-y-2">
        {navItems.map((item) => (
          <button
            key={item.label}
            type="button"
            className={`flex w-full items-center rounded-xl px-3 py-2.5 text-left text-sm font-medium transition ${
              item.active
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-300 dark:hover:bg-slate-800 dark:hover:text-white'
            }`}
          >
            {item.label}
          </button>
        ))}
      </nav>

      <div className="mt-auto rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-300">
        <p className="font-semibold text-slate-900 dark:text-slate-100">Ready for scale</p>
        <p className="mt-1 text-xs leading-5">Architecture is prepared for remote lab execution and future reports.</p>
      </div>
    </aside>
  );
}
