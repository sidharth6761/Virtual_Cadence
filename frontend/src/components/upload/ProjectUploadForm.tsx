import { useMemo, useState } from 'react';
import { StatusBanner } from '../ui/StatusBanner';
import { FileDropzone } from '../ui/FileDropzone';
import { uploadProject } from '../../services/api';
import type { UploadFileItem, UploadResponse, UploadState } from '../../types';

const initialState: UploadState = {
  isDragging: false,
  isUploading: false,
  progress: 0,
  message: null,
  messageType: null,
};

export function ProjectUploadForm() {
  const [designFiles, setDesignFiles] = useState<UploadFileItem[]>([]);
  const [constraintFile, setConstraintFile] = useState<File | null>(null);
  const [libraryFile, setLibraryFile] = useState<File | null>(null);
  const [topModule, setTopModule] = useState('top_module');
  const [clockPeriod, setClockPeriod] = useState('10');
  const [state, setState] = useState(initialState);

  const designFileCount = useMemo(() => designFiles.length, [designFiles.length]);

  const handleDesignSelection = (files: File[]) => {
    const nextFiles = files.map((file) => ({ id: `${file.name}-${file.size}`, file }));
    setDesignFiles((prev) => [...prev, ...nextFiles]);
  };

  const handleRemoveDesign = (index: number) => {
    setDesignFiles((prev) => prev.filter((_, itemIndex) => itemIndex !== index));
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!designFiles.length || !libraryFile) {
      setState({
        ...initialState,
        message: 'Please add at least one design file and a library file.',
        messageType: 'error',
      });
      return;
    }

    setState({ ...initialState, isUploading: true, progress: 10 });

    try {
      const response: UploadResponse = await uploadProject({
        designFiles: designFiles.map((item) => item.file),
        constraintFile,
        libraryFile,
        topModule,
        clockPeriod: Number(clockPeriod),
      });

      setState({
        isDragging: false,
        isUploading: false,
        progress: 100,
        message: 'Upload Successful',
        messageType: 'success',
        jobId: response.job_id,
        filesReceived: response.files_received,
        status: 'Uploaded',
      });
    } catch (error) {
      setState({
        ...initialState,
        message:
          error instanceof Error
            ? error.message
            : 'Upload failed. Please try again.',
        messageType: 'error',
      });
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {state.message ? (
        <StatusBanner type={state.messageType ?? 'success'} title={state.message}>
          {state.messageType === 'success' ? (
            <div className="mt-3 space-y-2 text-sm text-slate-700 dark:text-slate-300">
              <p>
                <span className="font-semibold">Job ID:</span> {state.jobId}
              </p>
              <p>
                <span className="font-semibold">Files Received:</span> {state.filesReceived}
              </p>
              <p>
                <span className="font-semibold">Status:</span> {state.status}
              </p>
            </div>
          ) : null}
        </StatusBanner>
      ) : null}

      <div className="grid gap-6 lg:grid-cols-[1.3fr_0.7fr]">
        <div className="space-y-6">
          <FileDropzone
            title="Design Files"
            description="Upload one or more Verilog/SystemVerilog sources"
            accept=".v, .sv"
            multiple
            files={designFiles.map((item) => item.file)}
            onFilesSelected={handleDesignSelection}
            onRemoveFile={handleRemoveDesign}
          />

          <div className="grid gap-6 md:grid-cols-2">
            <FileDropzone
              title="Constraint File"
              description="Optional SDC timing constraint"
              accept=".sdc"
              files={constraintFile ? [constraintFile] : []}
              onFilesSelected={(files) => setConstraintFile(files[0] ?? null)}
              onRemoveFile={() => setConstraintFile(null)}
              compact
            />
            <FileDropzone
              title="Library File"
              description="Technology or standard cell library"
              accept=".lib"
              files={libraryFile ? [libraryFile] : []}
              onFilesSelected={(files) => setLibraryFile(files[0] ?? null)}
              onRemoveFile={() => setLibraryFile(null)}
              compact
            />
          </div>
        </div>

        <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-950">
          <div className="mb-6">
            <p className="text-sm font-semibold text-slate-900 dark:text-slate-100">Project Summary</p>
            <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">Prepare the synthesis inputs for your next run.</p>
          </div>

          <div className="space-y-4">
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">
              Top Module Name
              <input
                value={topModule}
                onChange={(event) => setTopModule(event.target.value)}
                className="mt-2 w-full rounded-2xl border border-slate-300 bg-slate-50 px-3 py-2.5 text-sm outline-none ring-0 transition focus:border-blue-500 dark:border-slate-700 dark:bg-slate-900"
                placeholder="top_module"
              />
            </label>

            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">
              Clock Period (ns)
              <input
                type="number"
                min="1"
                step="0.1"
                value={clockPeriod}
                onChange={(event) => setClockPeriod(event.target.value)}
                className="mt-2 w-full rounded-2xl border border-slate-300 bg-slate-50 px-3 py-2.5 text-sm outline-none ring-0 transition focus:border-blue-500 dark:border-slate-700 dark:bg-slate-900"
              />
            </label>

            <div className="rounded-2xl border border-slate-200 bg-slate-50/70 p-3 text-sm text-slate-600 dark:border-slate-800 dark:bg-slate-900/70 dark:text-slate-300">
              <div className="flex items-center justify-between">
                <span>Design files</span>
                <span className="font-semibold text-slate-900 dark:text-slate-100">{designFileCount}</span>
              </div>
              <div className="mt-2 flex items-center justify-between">
                <span>Constraint</span>
                <span className="font-semibold text-slate-900 dark:text-slate-100">{constraintFile ? 'Ready' : 'Optional'}</span>
              </div>
              <div className="mt-2 flex items-center justify-between">
                <span>Library</span>
                <span className="font-semibold text-slate-900 dark:text-slate-100">{libraryFile ? 'Ready' : 'Pending'}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="rounded-3xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-950">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div className="flex items-center gap-3">
            <div className="h-2.5 w-2.5 rounded-full bg-blue-600" />
            <div>
              <p className="text-sm font-semibold text-slate-900 dark:text-slate-100">Upload progress</p>
              <p className="text-sm text-slate-500 dark:text-slate-400">Track the transfer status before the project is stored.</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="h-2.5 w-44 overflow-hidden rounded-full bg-slate-200 dark:bg-slate-800">
              <div className="h-full rounded-full bg-blue-600 transition-all" style={{ width: `${state.progress}%` }} />
            </div>
            <span className="text-sm font-medium text-slate-600 dark:text-slate-300">{state.progress}%</span>
          </div>
        </div>
      </div>

      <div className="flex flex-wrap gap-3">
        <button
          type="submit"
          disabled={state.isUploading}
          className="rounded-2xl bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {state.isUploading ? 'Uploading…' : 'Upload Project'}
        </button>
        <button
          type="button"
          onClick={() => {
            setDesignFiles([]);
            setConstraintFile(null);
            setLibraryFile(null);
            setTopModule('top_module');
            setClockPeriod('10');
            setState(initialState);
          }}
          className="rounded-2xl border border-slate-300 px-5 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-900"
        >
          Clear
        </button>
      </div>
    </form>
  );
}
