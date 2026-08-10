import { useMemo } from 'react';

interface FileDropzoneProps {
  title: string;
  description: string;
  accept: string;
  multiple?: boolean;
  files: File[];
  onFilesSelected: (files: File[]) => void;
  onRemoveFile: (index: number) => void;
  compact?: boolean;
}

export function FileDropzone({
  title,
  description,
  accept,
  multiple = false,
  files,
  onFilesSelected,
  onRemoveFile,
  compact = false,
}: FileDropzoneProps) {
  const fileList = useMemo(() => files.map((file) => ({ name: file.name, size: file.size })), [files]);

  return (
    <div className="rounded-2xl border border-slate-200 bg-slate-50/70 p-4 dark:border-slate-800 dark:bg-slate-900/70">
      <div className="mb-3 flex items-center justify-between">
        <div>
          <p className="text-sm font-semibold text-slate-900 dark:text-slate-100">{title}</p>
          <p className="text-sm text-slate-500 dark:text-slate-400">{description}</p>
        </div>
        <span className="rounded-full bg-slate-200 px-2.5 py-1 text-xs font-medium text-slate-700 dark:bg-slate-800 dark:text-slate-300">
          {accept}
        </span>
      </div>

      <label className={`flex cursor-pointer flex-col items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-white px-4 py-6 text-center transition hover:border-blue-500 hover:bg-blue-50/60 dark:border-slate-700 dark:bg-slate-950/50 dark:hover:border-blue-400 ${compact ? 'min-h-[120px]' : 'min-h-[148px]'}`}>
        <input
          type="file"
          accept={accept}
          multiple={multiple}
          className="hidden"
          onChange={(event) => {
            const selected = Array.from(event.target.files ?? []);
            if (selected.length) {
              onFilesSelected(selected);
            }
            event.target.value = '';
          }}
        />
        <div className="rounded-full bg-blue-600/10 p-2 text-blue-600 dark:text-blue-400">
          <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="1.8">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 16V4m0 0l-4 4m4-4l4 4M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2" />
          </svg>
        </div>
        <p className="mt-3 text-sm font-medium text-slate-700 dark:text-slate-200">Drop files here or click to browse</p>
        <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">Supports {accept}</p>
      </label>

      {fileList.length > 0 ? (
        <ul className="mt-3 space-y-2">
          {fileList.map((item, index) => (
            <li key={`${item.name}-${index}`} className="flex items-center justify-between rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm dark:border-slate-800 dark:bg-slate-950/70">
              <div>
                <p className="font-medium text-slate-800 dark:text-slate-200">{item.name}</p>
                <p className="text-xs text-slate-500 dark:text-slate-400">{(item.size / 1024).toFixed(1)} KB</p>
              </div>
              <button type="button" onClick={() => onRemoveFile(index)} className="text-sm text-slate-500 hover:text-rose-600">
                Remove
              </button>
            </li>
          ))}
        </ul>
      ) : null}
    </div>
  );
}
