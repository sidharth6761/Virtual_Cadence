import { useMemo } from 'react';

interface FileDropzoneProps {
  title: string;
  description?: string;
  accept: string;
  multiple?: boolean;
  files: File[];
  onFilesSelected: (files: File[]) => void;
  onRemoveFile: (index: number) => void;
}

function FileIcon({ type }: { type: string }) {
  if (type === 'rtl') {
    return (
      <svg viewBox="0 0 24 24" className="h-8 w-8 text-blue-500" fill="none" stroke="currentColor" strokeWidth="1.5">
        <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
      </svg>
    );
  }
  if (type === 'library') {
    return (
      <svg viewBox="0 0 24 24" className="h-8 w-8 text-blue-500" fill="none" stroke="currentColor" strokeWidth="1.5">
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" />
      </svg>
    );
  }
  return (
    <svg viewBox="0 0 24 24" className="h-8 w-8 text-blue-500" fill="none" stroke="currentColor" strokeWidth="1.5">
      <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
    </svg>
  );
}

function fileTypeFromAccept(accept: string): string {
  if (accept.includes('.v')) return 'rtl';
  if (accept.includes('.lib')) return 'library';
  return 'constraint';
}

export function FileDropzone({
  title,
  accept,
  multiple = false,
  files,
  onFilesSelected,
  onRemoveFile,
}: FileDropzoneProps) {
  const fileList = useMemo(() => files.map((file) => ({ name: file.name, size: file.size })), [files]);
  const fileType = fileTypeFromAccept(accept);

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5">
      <label className="flex cursor-pointer flex-col items-center justify-center rounded-lg border border-dashed border-slate-300 py-8 text-center transition hover:border-blue-400 hover:bg-blue-50/40">
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
        <FileIcon type={fileType} />
        <p className="mt-3 text-sm font-medium text-slate-700">{title}</p>
        <p className="mt-1 text-xs text-slate-500">Drop files or click to browse</p>
      </label>

      {fileList.length > 0 ? (
        <ul className="mt-3 space-y-2">
          {fileList.map((item, index) => (
            <li key={`${item.name}-${index}`} className="flex items-center justify-between rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm">
              <div>
                <p className="font-medium text-slate-800">{item.name}</p>
                <p className="text-xs text-slate-500">{(item.size / 1024).toFixed(1)} KB</p>
              </div>
              <button type="button" onClick={() => onRemoveFile(index)} className="text-xs text-slate-500 hover:text-rose-600">
                Remove
              </button>
            </li>
          ))}
        </ul>
      ) : null}
    </div>
  );
}
