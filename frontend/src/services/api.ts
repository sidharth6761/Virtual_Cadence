import { supabase, BUCKET } from '../supabase/client';
import type { UploadResponse } from '../types';

function sanitizeFilename(name: string): string {
  const base = String(name || '').split('/').pop()?.split('\\').pop() ?? '';
  return base.replace(/^\.+/, '').replace(/[^\w.-]/g, '_').slice(0, 255);
}

function fileTypeFromName(name: string): string {
  const ext = name.split('.').pop()?.toLowerCase() ?? '';
  if (ext === 'v' || ext === 'sv') return 'rtl';
  if (ext === 'lib') return 'library';
  if (ext === 'sdc') return 'constraint';
  return 'other';
}

const now = () => new Date().toISOString();

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
}): Promise<UploadResponse> => {
  void clockPeriod;

  // 1. Create the project row (anonymous)
  const { data: project, error: projectError } = await supabase
    .from('projects')
    .insert({ name: `${topModule || 'Synthesis'} Project`, created_at: now(), updated_at: now() })
    .select('id')
    .single();
  if (projectError) throw new Error(projectError.message);

  // 2. Create the job row (UPLOADING)
  const { data: job, error: jobError } = await supabase
    .from('jobs')
    .insert({ project_id: project.id, status: 'UPLOADING', created_at: now(), updated_at: now() })
    .select('id')
    .single();
  if (jobError) throw new Error(jobError.message);

  const jobId = String(job.id).padStart(4, '0');
  const root = `jobs/JOB_${jobId}`;

  // 3. Upload each file to Supabase Storage
  const allFiles: File[] = [...designFiles];
  if (constraintFile) allFiles.push(constraintFile);
  allFiles.push(libraryFile);

  const metadata: { filename: string; storage_path: string; file_type: string; file_size: number }[] = [];

  for (const file of allFiles) {
    const filename = sanitizeFilename(file.name);
    const storagePath = `${root}/${filename}`;
    const { error: uploadError } = await supabase.storage
      .from(BUCKET)
      .upload(storagePath, file, { cacheControl: '3600', upsert: true });
    if (uploadError) throw new Error(`Failed to upload '${filename}': ${uploadError.message}`);
    metadata.push({
      filename,
      storage_path: storagePath,
      file_type: fileTypeFromName(filename),
      file_size: file.size,
    });
  }

  // 4. Record file metadata
  const { error: filesError } = await supabase.from('files').insert(
    metadata.map((meta) => ({ ...meta, job_id: job.id, created_at: now() })),
  );
  if (filesError) throw new Error(filesError.message);

  // 5. Mark job QUEUED
  const { error: queueError } = await supabase
    .from('jobs')
    .update({ status: 'QUEUED', updated_at: now() })
    .eq('id', job.id);
  if (queueError) throw new Error(queueError.message);

  return {
    success: true,
    job_id: `JOB_${jobId}`,
    files_received: metadata.length,
    upload_path: `design-files/${root}`,
  };
};