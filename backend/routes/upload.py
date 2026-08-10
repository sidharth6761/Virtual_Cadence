from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.app.core.config import settings
from backend.app.core.security import decode_access_token
from backend.app.database.db import get_connection
from backend.app.services.storage_service import storage_service
from backend.models.upload import JobMetadata, UploadResponse
from backend.services.storage import validate_supported_file

router = APIRouter(tags=["upload"])
security = HTTPBearer(auto_error=False)


def _normalize_filename(upload_file: UploadFile) -> str:
    return Path(upload_file.filename or "").name


def _validate_unique_filenames(files: Iterable[UploadFile]) -> None:
    names = [_normalize_filename(upload_file) for upload_file in files if upload_file.filename]
    duplicates = {name for name in names if names.count(name) > 1}
    if duplicates:
        raise HTTPException(
            status_code=400,
            detail=f"Duplicate filenames detected in the same upload: {', '.join(sorted(duplicates))}",
        )


def _validate_file_size(upload_file: UploadFile) -> None:
    settings.refresh()
    if upload_file.file is None:
        return
    if not hasattr(upload_file.file, "seek"):
        return
    upload_file.file.seek(0, 2)
    size_bytes = upload_file.file.tell()
    upload_file.file.seek(0)
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if size_bytes > max_bytes:
        raise HTTPException(status_code=413, detail=f"File exceeds the {settings.max_upload_size_mb}MB limit")


def _get_user_id(credentials: HTTPAuthorizationCredentials | None) -> int | None:
    if not credentials:
        return None
    try:
        payload = decode_access_token(credentials.credentials)
        return int(payload["sub"])
    except Exception:
        return None


@router.post("/upload", response_model=UploadResponse)
async def upload_project(
    design_files: list[UploadFile] = File(default=[]),
    library_file: UploadFile | None = File(default=None),
    constraint_file: UploadFile | None = File(default=None),
    top_module: str = Form(...),
    clock_period: float = Form(...),
    project_id: int | None = Form(default=None),
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> UploadResponse:
    all_files: list[UploadFile] = [*design_files]
    if library_file is not None:
        all_files.append(library_file)
    if constraint_file is not None:
        all_files.append(constraint_file)

    if not all_files:
        raise HTTPException(status_code=400, detail="No files selected. Please upload at least one supported file.")

    _validate_unique_filenames(all_files)

    for upload_file in all_files:
        validate_supported_file(upload_file.filename or "")
        _validate_file_size(upload_file)

    user_id = _get_user_id(credentials)
    created_at = datetime.now(timezone.utc).isoformat()
    conn = get_connection()
    try:
        if user_id is not None:
            project_row = conn.execute(
                "SELECT id FROM projects WHERE id = ? AND user_id = ?",
                (project_id, user_id),
            ).fetchone() if project_id is not None else None
            if project_row is None:
                project_cursor = conn.execute(
                    "INSERT INTO projects (user_id, name, created_at) VALUES (?, ?, ?)",
                    (user_id, f"{top_module or 'upload'} Project", created_at),
                )
                project_id = int(project_cursor.lastrowid)
            else:
                project_id = int(project_row["id"])
        else:
            project_cursor = conn.execute(
                "INSERT INTO projects (user_id, name, created_at) VALUES (?, ?, ?)",
                (None, f"{top_module or 'upload'} Project", created_at),
            )
            project_id = int(project_cursor.lastrowid)

        job_cursor = conn.execute(
            "INSERT INTO jobs (project_id, status, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (project_id, "UPLOADING", created_at, created_at),
        )
        job_db_id = int(job_cursor.lastrowid)
        job_id = f"JOB_{job_db_id:04d}"

        saved_file_names: list[str] = []
        for upload_file in all_files:
            saved_name = storage_service.save_upload(job_id, upload_file)
            saved_file_names.append(saved_name)
            conn.execute(
                "INSERT INTO files (job_id, filename, stored_name, created_at) VALUES (?, ?, ?, ?)",
                (job_db_id, _normalize_filename(upload_file), saved_name, created_at),
            )

        conn.execute(
            "UPDATE jobs SET status = ?, updated_at = ? WHERE id = ?",
            ("UPLOADED", created_at, job_db_id),
        )
        conn.commit()

        metadata = JobMetadata(job_id=job_id, created_at=created_at, status="UPLOADED", files=saved_file_names)
        storage_service.save_metadata_file(job_id, metadata.model_dump_json(indent=2))

        return UploadResponse(
            success=True,
            job_id=job_id,
            files_received=len(saved_file_names),
            upload_path=f"storage/jobs/{job_id}",
        )
    except HTTPException:
        raise
    except Exception as error:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(error)) from error
    finally:
        conn.close()
