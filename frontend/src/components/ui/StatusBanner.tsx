import type { ReactNode } from 'react';

interface StatusBannerProps {
  type: 'success' | 'error';
  title: string;
  children?: ReactNode;
}

const styles = {
  success: 'border-emerald-500/20 bg-emerald-500/10 text-emerald-700 dark:text-emerald-300',
  error: 'border-rose-500/20 bg-rose-500/10 text-rose-700 dark:text-rose-300',
};

export function StatusBanner({ type, title, children }: StatusBannerProps) {
  return (
    <div className={`rounded-2xl border px-4 py-3 text-sm ${styles[type]}`}>
      <p className="font-medium">{title}</p>
      {children ? <div className="mt-1">{children}</div> : null}
    </div>
  );
}
