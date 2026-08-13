import { useState } from 'react';
import { StatusBanner } from '../ui/StatusBanner';
import { FileDropzone } from '../ui/FileDropzone';
import { uploadProject } from '../../services/api';
import type { UploadResponse, UploadState } from '../../types';

const initialState: UploadState = {
  isDragging: false,
  isUploading: false,
  progress: 0,
  message: null,
  messageType: null,
};

export function ProjectUploadForm() {
  const [designFiles, setDesignFiles] = useState<File[]>([]);
  const [constraintFile, setConstraintFile] = useState<File | null>(null);
  const [libraryFile, setLibraryFile] = useState<File | null>(null);
  const [topModule, setTopModule] = useState('top_module');
  const [clockPeriod, setClockPeriod] = useState('10');
  const [state, setState] = useState(initialState);

  const handleDesignSelection = (files: File[]) => {
    setDesignFiles((prev) => [...prev, ...files]);
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
        designFiles,
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
            <div className="mt-3 space-y-1 text-sm text-slate-700">
              <p><span className="font-semibold">Job ID:</span> {state.jobId}</p>
              <p><span className="font-semibold">Files Received:</span> {state.filesReceived}</p>
              <p><span className="font-semibold">Status:</span> {state.status}</p>
            </div>
          ) : null}
        </StatusBanner>
      ) : null}

      <div className="grid gap-4 sm:grid-cols-3">
        <FileDropzone
          title="Design Files (.v)"
          description="Drop files or click to browse"
          accept=".v, .sv"
          multiple
          files={designFiles}
          onFilesSelected={handleDesignSelection}
          onRemoveFile={(index) => setDesignFiles((prev) => prev.filter((_, i) => i !== index))}
        />
        <FileDropzone
          title="Technology Library (.lib)"
          description="Drop files or click to browse"
          accept=".lib"
          files={libraryFile ? [libraryFile] : []}
          onFilesSelected={(files) => setLibraryFile(files[0] ?? null)}
          onRemoveFile={() => setLibraryFile(null)}
        />
        <FileDropzone
          title="Constraints (.sdc)"
          description="Drop files or click to browse"
          accept=".sdc"
          files={constraintFile ? [constraintFile] : []}
          onFilesSelected={(files) => setConstraintFile(files[0] ?? null)}
          onRemoveFile={() => setConstraintFile(null)}
        />
      </div>

      <div className="flex items-center gap-4">
        <input
          type="hidden"
          value={topModule}
          onChange={(e) => setTopModule(e.target.value)}
        />
        <input
          type="hidden"
          value={clockPeriod}
          onChange={(e) => setClockPeriod(e.target.value)}
        />
        <button
          type="submit"
          disabled={state.isUploading}
          className="w-full rounded-lg bg-blue-600 px-6 py-3 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {state.isUploading ? 'Uploading...' : 'Submit Synthesis Job'}
        </button>
      </div>
    </form>
  );
}
