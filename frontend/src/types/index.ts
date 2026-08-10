export interface UploadFileItem {
  id: string;
  file: File;
}

export interface UploadResponse {
  success: boolean;
  job_id: string;
  files_received: number;
  upload_path: string;
}

export interface UploadState {
  isDragging: boolean;
  isUploading: boolean;
  progress: number;
  message: string | null;
  messageType: 'success' | 'error' | null;
  jobId?: string;
  filesReceived?: number;
  status?: string;
}
