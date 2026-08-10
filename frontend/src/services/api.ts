import axios from 'axios';
import type { UploadResponse } from '../types';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000',
  timeout: 600000,
});

export const uploadProject = async ({
  designFiles,
  constraintFile,
  libraryFile,
  topModule,
  clockPeriod,
}: {
  designFiles: File[];
  constraintFile?: File | null;
  libraryFile: File;
  topModule: string;
  clockPeriod: number;
}) => {
  const formData = new FormData();

  designFiles.forEach((file) => {
    formData.append('design_files', file);
  });

  if (constraintFile) {
    formData.append('constraint_file', constraintFile);
  }

  if (!libraryFile) {
    throw new Error('Library file is required.');
  }

  formData.append('library_file', libraryFile);
  formData.append('top_module', topModule);
  formData.append('clock_period', String(clockPeriod));

  const response = await api.post<UploadResponse>('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (event) => {
      if (event.total) {
        return Math.round((event.loaded * 100) / event.total);
      }
    },
  });

  return response.data;
};
