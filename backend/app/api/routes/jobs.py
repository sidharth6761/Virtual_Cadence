from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.app.core.security import decode_access_token
from backend.app.database.db import get_connection
from backend.app.schemas.job import JobCreateRequest, JobResponse

router = APIRouter(prefix="/api/jobs", tags=["jobs"])
security = HTTPBearer()


def get_current_user_id(credentials: HTTPAuthorizationCredentials) -> int:
    try:
        token_payload = decode_access_token(credentials.credentials)
        return int(token_payload["sub"])
    except Exception as error:
        raise HTTPException(status_code=401, detail="Invalid token") from error


@router.post("", response_model=JobResponse)
def create_job(payload: JobCreateRequest, credentials: HTTPAuthorizationCredentials = Depends(security)) -> JobResponse:
    user_id = get_current_user_id(credentials)
    conn = get_connection()
    try:
        project = conn.execute(
            "SELECT id FROM projects WHERE id = ? AND user_id = ?",
            (payload.project_id, user_id),
        ).fetchone()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        now = datetime.now(timezone.utc).isoformat()
        cursor = conn.execute(
            "INSERT INTO jobs (project_id, status, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (payload.project_id, "CREATED", now, now),
        )
        conn.commit()
        job_id = f"JOB_{int(cursor.lastrowid):04d}"
        return JobResponse(
            id=int(cursor.lastrowid),
            project_id=payload.project_id,
            status="CREATED",
            created_at=now,
            updated_at=now,
            job_id=job_id,
        )
    finally:
        conn.close()


@router.get("", response_model=list[JobResponse])
def list_jobs(credentials: HTTPAuthorizationCredentials = Depends(security)) -> list[JobResponse]:
    user_id = get_current_user_id(credentials)
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT j.id, j.project_id, j.status, j.created_at, j.updated_at
            FROM jobs j
            JOIN projects p ON p.id = j.project_id
            WHERE p.user_id = ?
            ORDER BY j.created_at DESC
            """,
            (user_id,),
        ).fetchall()
        return [
            JobResponse(
                id=int(row["id"]),
                project_id=int(row["project_id"]),
                status=row["status"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                job_id=f"JOB_{int(row['id']):04d}",
            )
            for row in rows
        ]
    finally:
        conn.close()


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)) -> JobResponse:
    user_id = get_current_user_id(credentials)
    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT j.id, j.project_id, j.status, j.created_at, j.updated_at
            FROM jobs j
            JOIN projects p ON p.id = j.project_id
            WHERE j.id = ? AND p.user_id = ?
            """,
            (int(job_id.replace("JOB_", "")) if job_id.startswith("JOB_") else int(job_id), user_id),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Job not found")
        return JobResponse(
            id=int(row["id"]),
            project_id=int(row["project_id"]),
            status=row["status"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            job_id=f"JOB_{int(row['id']):04d}",
        )
    finally:
        conn.close()
